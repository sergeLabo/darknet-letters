#!/usr/bin/env python3
# -*- coding: utf8 -*-

########################################################################
# This file is part of Darknet Midi.
#
# Darknet Midi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Darknet Midi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
########################################################################


"""
Utilise FluidR3_GM.sf2 uniquement.

Installation:
    numpy
    pretty_midi
    fluidsynth
    FluidR3_GM.sf2
    
Le dossier music doit exister avec des morceaux midi.
"""


import os, sys
from time import sleep
import pathlib
import threading
import json
from random import choice
import numpy as np

import mido

sys.path.append("/media/data/3D/projets/darknet-letters/letters/midi/my_pretty_midi/")
import my_pretty_midi

import fluidsynth

# TODO: chemin à revoir


class PlayOneMidiNote:
    """Ne fonctionne qu'avec FluidR3_GM.sf2
    note et volume entre 0 et 127
    Pas de variation de volume en cours de note
    """
    
    def __init__(self, fonts, channel, bank, bank_number):
        """self.channel 1 to 16
        fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
        bank = 0, il y a d'autres bank dans FluidR3_GM.sf2
                    mais pas toujours avec 128 instruments
        bank_number = 0 à 127,
                        idem pas toujours 128 instruments par bank_number

        self.thread_dict = {69: 1, 48: 1, 78:0}           
        """
        
        # 1 objet PlayOneMidiNote = 1 channel
        self.channel = channel
        
        self.fonts = fonts
        self.bank = bank
        self.bank_number = bank_number

        self.set_audio()
        self.thread_dict = {}
        self.nbr = 0
            
    def set_audio(self):
        """Spécifique à FluidR3_GM.sf2
        note from 0 to 127 but all values are not possible in all bank
        life 0 to ?
        channel 1 to 16
        volume 0 to 127

        yamaha grand piano
           program_select(channel,  sfid, bank, bank number)
        fs.program_select(  1  ,    sfid,  0,      0       )
        """

        self.fs = fluidsynth.Synth()
        self.fs.start(driver='alsa')
        sfid = self.fs.sfload(self.fonts)
        self.fs.program_select(self.channel, sfid, self.bank, self.bank_number)

    def play_note(self, note, volume):
        """Lancé par le thread thread_note
        Se termine si self.thread_dict[note] = 0
        """

        # Excécution de la note
        self.fs.noteon(self.channel, note, volume)

        # Boucle qui tourne en rond en attendant
        # self.thread_dict[(note, volume)] = 0
        while self.thread_dict[note]:
            # Tourne en rond
            sleep(0.0001)
            
        # Sinon fin de la note
        print("      Fin du thread: channel =", self.channel,
                                      "note =", note,
                                    "volume =", volume)
                               
        self.fs.noteoff(self.channel, note)
        self.nbr -= 1
        
        # Supression de la clé du dict
        del self.thread_dict[note]

    def thread_note(self, note, volume):
        """Le thread se termine si self.thread_dict[(note, volume)]=0
        note et volume entre 0 et 127
        """

        note, volume = cut_the_top_off_note_volume(note, volume)
        
        # Excécution de la note si elle n'est pas en cours
        if note not in self.thread_dict:
            self.thread_dict[note] = 1
            
            print("Lancement du thread: channel =", self.channel,
                                        "note =", note,
                                        "volume =", volume)

            self.nbr += 1                    
            thread = threading.Thread(target=self.play_note,
                                      args=(note, volume))
            thread.start()
            
        
class PlayOneMidiPartition:
    """Ne fonctionne qu'avec FluidR3_GM.sf2"""

    def __init__(self, fonts, channel, bank, bank_number):
        """self.channel 1 to 16
        channel 10 pour les drums
        """

        self.fonts = fonts
        self.channel = channel
        self.bank = bank
        self.bank_number = bank_number

        self.set_audio()
        self.thread_dict = {}
        for i in range(128):
            self.thread_dict[i] = 0

    def set_audio(self):
        """Spécifique à FluidR3_GM.sf2
        note from 0 to 127 but all values are not possible in all bank
        life 0 to ?
        channel 1 to 16
        volume 0 to 127

        yamaha grand piano
           program_select(channel,  sfid, bank, bank number)
        fs.program_select(  1  ,    sfid,  0,      0       )
        """

        self.fs = fluidsynth.Synth()
        self.fs.start(driver='alsa')
        sfid = self.fs.sfload(self.fonts)
        self.fs.program_select(self.channel, sfid, self.bank, self.bank_number)

    def play_note(self, note, volume):
        """Lancé par le thread thread_note
        Se termine si self.thread_dict[note] = 0
        """
        
        self.fs.noteon(self.channel, note, volume)
        while self.thread_dict[note]:
            # Pour rester dans cette boucle
            sleep(0.0001)
        # Sinon fin de la note
        self.fs.noteoff(self.channel, note)

    def thread_note(self, note, volume):
        """Le thread se termine si note_off"""

        self.thread_dict[note] = 1
        thread = threading.Thread(target=self.play_note, args=(note, volume))
        thread.start()

    def play_partition(self, partition, FPS):
        """partition = liste de listes (note=82, velocity=100)
        [[(82,100)], [(82,100), (45,88)], [(0,0)], ...
        un item tous les 1/FPS
        """

        for event in partition:
            # event sont les notes pour la frame
            nombre_de_note = len(event)
            note_en_cours = []
            for midi in range(nombre_de_note):
                note = int(event[midi][0])
                note_en_cours.append(note)
                volume = int(event[midi][1])

                # Lancement de la note si pas en cours
                if self.thread_dict[note] == 0:
                    self.thread_note(note, volume)

            # Fin des notes autres que les notes en cours
            for k, v in self.thread_dict.items():
                if v == 1:
                    if k not in note_en_cours:
                        self.thread_dict[k] = 0
                        
            sleep(1/FPS)

        self.the_end()

    def the_end(self):
        """Bombe atomique: Fin  de tous les threads"""

        for i in range(128):
            self.thread_dict[i] = 0


class AnalyseMidiFile:
    """Analyse le fichier midi,
    trouve le nombre et le nom des instruments.
    Retourne la liste des notes sur une time lapse de chaque instrument.
    save_midi_json enregistre le midi en json

    partitions = liste des partitions
    instruments = liste des instruments soit objet avec .program et .name
    """

    def __init__(self, midi_file, FPS):
        """Un seul fichier midi
        FPS de 10 à 1000, 50 ou 100 est bien
        Plus le FPS est élevé, plus le temps de calcul est long !
        """

        print("\nAnalyse de", midi_file)
        
        self.midi_file = midi_file
        self.FPS = FPS
        self.end_time = 0
        self.instruments = None
        self.instrum_new = []
        self.partitions = []
                
    def get_instruments(self):
        """instruments =
        [Instrument(program=71, is_drum=False, name="Grand Piano"), ...]
        """

        # Récupération des datas avec pretty_midi
        midi_pretty_format = my_pretty_midi.PrettyMIDI(self.midi_file)
        
        # Supprime les notes avec fin avant le début !
        midi_pretty_format.remove_invalid_notes()

        # Time de fin, instruments du fichier
        self.end_time = midi_pretty_format.get_end_time()
        self.instruments = midi_pretty_format.instruments

        # Correction des intruments pour avoir le program des drums
        self.instruments_with_drums()
        
        print("\nListe des instruments:")
        for instrument in self.instruments:
            ins = self.instrum_new[self.instruments.index(instrument)]
            print("   ", instrument, "soit", ins)
        print("\n")

    def instruments_with_drums(self):
        """"De:
            [Instrument(program=25, is_drum=False, name="Bass"),
             Instrument(program=0, is_drum=True, name="Drums"),
             Instrument(program=0, is_drum=True, name="Drums2")]
             
            pour une liste de tuple:
            [((0, 25), False, "Bass"),
             ((0, 116), True, "Drums"),
             ((8, 115), True, "Drums2")]
             
        Pour le dict du json
        "instruments": [[(0, 25), false], [(0, 116), true], [(8, 116), true]]}
        """
        
        for instrument in self.instruments:
            program = instrument.program
            is_drum = instrument.is_drum
            name = instrument.name
            
            if is_drum:
                bank, bank_nbr = self.get_drum_program()
            else:
                bank = 0
                bank_nbr = int(program)
            self.instrum_new.append(((bank, bank_nbr), is_drum, name))
            
        print("Instrument corrigé", self.instrum_new)
                
    def get_drum_program(self):
        """ Cas possible:
                0 114 Steel Drums
                0 115 Woodblock
                0 116 Taiko Drum
                0 117 Melodic Tom
                0 118 Synth Drum
                0 119 Reverse Cymbal
                8 116 Concert Bass Drum
                8 117 Melo Tom 2
                8 118 808 Tom
        """

        drums = [(0, 114),
                 (0, 115),
                 (0, 116),
                 (0, 117),
                 (0, 118),
                 (0, 119),
                 (8, 116),
                 (8, 117),
                 (8, 118)]
        
        return choice(drums)
        
    def get_partitions(self):
        """Fait les étapes pour tous les instruments,
        retourne les instruments et leurs partitions.
        """

        # Si fichier midi anormal
        try:
            self.get_instruments()
        except:
            print("Instruments non récupérable dans le fichier midi\n")
            self.instruments = []

        for instrument in self.instruments:
            print("Analyse du numéro d'instrument:", instrument.program,
                  "is_drum:", instrument.is_drum,
                  "name", instrument.name)

            # Array de 128 x nombre de frames
            instrument_roll = self.get_instrument_roll(instrument)

            # Conversion dans une liste de listes python
            partition = self.get_partition(instrument_roll, instrument)
            self.partitions.append(partition)
        
    def get_partition(self, instrument_roll, instrument):
        """Conversion du numpy array en liste de note à toutes les frames:

        une ligne par frame

        une ligne du array: (0.0 0.0 0.0 ... 89 ... 91 ... 0.0)
                                             89 est à la position 54
                                                    91 est à la position 68

        une ligne de la liste: 2 notes du même instrument 54 et 68
            [(54, 89), (68, 91)] = [(note=54, volume=89), (note=68, volume=91)]
        """

        # Copie des lignes du array dans une liste de ligne
        lignes = []
        for i in range(instrument_roll.shape[1]):
            ligne = instrument_roll[:, i]
            lignes.append(ligne)

        # Analyse des lignes pour ne garder que les non nuls
        partition = []
        for ligne in lignes:
            notes = []
            for n in range(128):
                if np.any(ligne[n] != np.float64(0)):
                    if not np.isnan(ligne[n]): # nan <class 'numpy.float64'>
                        velocity = int(ligne[n])
                        notes.append((n, velocity))
            
            partition.append(notes)

        # velocity maxi entre 0 et 127
        partition = normalize_velocity(partition)
        
        return partition

    def get_instrument_roll(self, partition):
        """Retourne un np.array de (128, FPS*durée du morceau en secondes)"""

        # La méthode get_piano_roll marche pour tous les instruments
        instrument_roll = partition.get_piano_roll(self.FPS,
                                                   np.arange(0,
                                                             self.end_time,
                                                             1/self.FPS))

        return instrument_roll

    def save_midi_json(self):
        """
        partitions = liste des partitions = [partition_1, partition_2 ...]
        instruments = [Instrument(program=71, is_drum=False, name="mélodie"),
                        ...]
            
        json_data = {"partitions":  [partition_1, partition_2 ......],
                     "instruments": [instrument_1.program,
                                     instrument_2.program, ...]
                      instrument is not JSON serializable = objet pretty_midi           
        """
                
        json_data = {}
        json_data["partitions"] = self.partitions
        json_data["instruments"] = []

        # #[((0, 25), False, "Bass"),
        # #((0, 116), True, "Drums"),
        # #((8, 115), True, "Drums2")]
        
        for i in range(len(self.instrum_new)):
            instrument_data = self.instrum_new[i]
            json_data["instruments"].append(instrument_data)

        # /media/data/3D/projets/darknet-letters/letters/midi/json/Quizas.json
        l = self.midi_file.split(".")
        name = l[0]
        name = name.replace("music", "json")
        file_name =  name + ".json"
        
        with open(file_name, 'w') as f_out:
            json.dump(json_data, f_out)
    
        print('\nEnregistrement de:', file_name)


class AnalyseAndPlay:

    def __init__(self, midi, FPS, fonts):
        """Fichier midi et FPS"""

        self.midi = midi
        self.FPS = FPS
        self.fonts = fonts
        self.partitions = []
        self.analyse_and_play()

    def analyse_and_play(self):
        amf = AnalyseMidiFile(self.midi, self.FPS)
        self.partitions, self.instruments = amf.get_partitions()
        print("Fin de l'analyse des partitions:")
        print("    Nombre de partition", len(self.partitions))

        for i in range(len(self.partitions)):
            # On ne peut utiliser que la bank 0 qui comprend 128 instruments
            channel = 0
            bank = 0
            if not self.instruments[i].is_drum:
                bank_number = self.instruments[i].program
                program = self.partitions[i]
            else:
                bank_number = 116
                program = self.partitions[i]
                
            self.thread_play_partition(channel,
                                       bank,
                                       bank_number,
                                       self.partitions[i])

        sleep(len(self.partitions[0])/100)
        print("Fin du fichier", file_list[n])
            
    def play_partition(self, channel, bank, bank_number, partition):
        pomp = PlayOneMidiPartition(self.fonts, channel, bank, bank_number)
        pomp.play_partition(partition, self.FPS)

    def thread_play_partition(self, channel, bank, bank_number, partition):
        """Le thread se termine si note_off"""

        thread = threading.Thread(target=self.play_partition, args=(
                                                                channel,
                                                                bank,
                                                                bank_number,
                                                                partition))
        thread.start()


class PlayJsonMidi:

    def __init__(self, midi_json, FPS, fonts):
        """midi_json créé avec AnalyseMidiFile"""

        self.midi_json = midi_json
        self.partitions, self.instruments = self.get_data_json(midi_json)
        self.FPS = FPS
        self.fonts = fonts

    def get_data_json(self, midi_json):
        """
        json_data = {"partitions":  [partition_1, partition_2 ......],
                     "instruments": [instrument_1.program,
                                     instrument_2.program, ...]
        """
        
        with open(self.midi_json) as f:
            data = json.load(f)

        partitions = data["partitions"]
        instruments = data["instruments"]
        
        return partitions, instruments

    def get_channel(self):
        """16 channel maxi
        channel 9 pour drums
        Les channels sont attribués dans l'ordre des instruments de la liste
        """
        
        channels = []
        channels_no_drum = [1,2,3,4,5,6,7,8,10,11,12,13,14,15,16]
        nbr = 0
        for instrument in self.instruments:
            if not instrument[1]:  # instrument[1] = boolean
                channels.append(channels_no_drum[nbr])
                nbr += 1
                if nbr == 16: nbr = 0
            else:
                channels.append(9)
        return channels
        
    def play(self):
        """Appelée pour jouer le json"""
        
        channels = self.get_channel()
        
        print("\nNombre de partitions", len(self.partitions))
        
        for i in range(len(self.partitions)):
            # [[0, 117], true, "Drums2"]
            chan = channels[i]
            is_drum = self.instruments[i][1]
            bank = self.instruments[i][0][0]
            bank_number = self.instruments[i][0][1]
            
            partition = self.partitions[i]
            
            print("    Channel:", chan, ", is_drum:", is_drum,
                  ", numéro d'instrument:", bank_number)
            
            self.thread_play_partition(chan, bank, bank_number, partition)

    def play_partition(self, channel, bank, bank_number, partition):
        """
        bank = 0
        bank_number = instrument[]
        partition = [[(82,100)], [(82,100), (45,88)], [(0,0)], ...
        """
        
        pomp = PlayOneMidiPartition(self.fonts, channel, bank, bank_number)
        pomp.play_partition(partition, self.FPS)

    def thread_play_partition(self, channel, bank, bank_number, partition):
        """Le thread se termine si note_off"""

        thread = threading.Thread(target=self.play_partition,
                                  args=(channel,
                                        bank,
                                        bank_number,
                                        partition))
        thread.start()


def normalize_velocity(partition):
    """partition[0] = [[couple], [couple]]"""

    # Recherche du volume maxi
    volume_maxi = 0
    for couple in partition:
        if couple:
            if couple[0][1] > volume_maxi:
                volume_maxi = couple[0][1]
                
    print("Volume maxi =", volume_maxi)
    
    # Correction du volume
    if volume_maxi > 127:
        print("    Correction du volume")
        for couple in partition[0]:
            note = couple[0]
            # print(couple, couple[0])  # (77, 45) 77
            correct = (couple[1] * 127) / volume_maxi
            partition[0][partition[0].index(couple)] = (note, correct)

    return partition

    
def cut_the_top_off_note_volume(note, volume):
    # note entre 0 et 127, volume entre 0 et maxi
    maxi = 127
    if note < 0: note = 0
    if note > 127: note = 127
    if volume < 0: volume = 0
    if volume > maxi: volume = maxi
    return note, volume

        
# Tous les tests
def get_file_list(directory, extentions):
    """Retourne la liste de tous les fichiers avec les extentions de
    la liste extentions
    """
    
    file_list = []
    for path, subdirs, files in os.walk(directory):
        for name in files:
            for extention in extentions:
                if name.endswith(extention):
                    file_list.append(str(pathlib.PurePath(path, name)))

    return file_list

    
def create_all_json(file_list, FPS):
    """Création des json des fichiers midi de file_list"""
    
    for midi in file_list:
        create_one_json(midi, FPS)


def create_one_json(midi_file, FPS):
    """Création d'un json"""
    
    amf = AnalyseMidiFile(midi_file, FPS)
    amf.get_partitions()
    amf.save_midi_json()


def play_json(json_file, FPS, fonts):
    """Joue un json"""

    print("\nPlay:", json_file)
    pjm = PlayJsonMidi(json_file, FPS, fonts)
    pjm.play()


def analyse_play_one_midi(midi_file):
    """Pour analyser et jouer"""
    
    aap = AnalyseAndPlay(midi_file, FPS, fonts)

    
if __name__ == '__main__':
    
    # FPS de 10 (trop petit) à 100 (très bien)
    FPS = 60

    # Il faut installer FluidR3_GM.sf2
    fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

    root = "/media/data/3D/projets/darknet-letters/letters"
    
    # Création des json
    directory = root + "/midi/music"
    extentions = [".midi", "mid"]
    file_list = get_file_list(directory, extentions)  
    create_all_json(file_list, FPS)

    # ## Joue le 1er json
    # #directory = root + "/midi/json"
    # #extentions = [".json"]
    # #file_list = get_file_list(directory, extentions)
    # #json_file = file_list[0]
    # #play_json(json_file, FPS, fonts)

    # ## Analyse et play
    # #directory = root + "/midi/music"
    # #extentions = [".mid", ".midi"]
    # #file_list = get_file_list(directory, extentions)
    # #midi_file = file_list[0]
    # #analyse_play_one_midi(midi_file)

    # ## Crée un json
    # #directory = root + "/midi/music"
    # #extentions = [".mid", ".midi"]
    # #file_list = get_file_list(directory, extentions)
    # #midi_file = file_list[0]
    # #create_one_json(midi_file, FPS)
