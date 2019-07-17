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


import os
from time import time, sleep
import pathlib
from random import randint, choice
import threading
import json
import numpy as np
import pretty_midi
import fluidsynth

# TODO: chemin à revoir

class PlayOneMidiNote:
    """Ne fonctionne qu'avec FluidR3_GM.sf2"""

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
        print("Fin du thread: channel=", self.channel, "note=", note)
        self.fs.noteoff(self.channel, note)

        # Supression de la clé du dict
        del self.thread_dict[note]

    def thread_note(self, note, volume):
        """Le thread se termine si self.thread_dict[note]=0"""

        print("Lancement du thread: channel=", self.channel, "note=", note)
        
        self.thread_dict[note] = 1
        thread = threading.Thread(target=self.play_note, args=(note, volume))
        thread.start()
        
            
class PlayOneMidiPartition:
    """Ne fonctionne qu'avec FluidR3_GM.sf2"""

    def __init__(self, fonts, bank, bank_number):
        """self.channel 1 to 16
        TODO Sert à quoi ?
        """

        self.fonts = fonts
        self.channel = 1
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

        self.midi_file = midi_file
        self.FPS = FPS
        self.end_time = 0
        print("\nAnalyse de", midi_file)
        
    def get_partitions(self):
        """Fait les étapes pour tous les instruments"""

        instruments = self.get_instruments()
        partitions = []
        for instrument in instruments:
            print("Analyse de:", instrument.program, "soit", instrument.name)
            instrument_roll = self.get_instrument_roll(instrument)
            partition = self.get_partition(instrument_roll, instrument)
            partitions.append(partition)

        return partitions, instruments

    def save_midi_json(self, partitions, instruments):
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
        json_data["partitions"] = partitions

        json_data["instruments"] = []
        # index ne marche pas
        for i in range(len(instruments)):
            # instruments[i].program est un attribut de pretty_midi
            json_data["instruments"].append(int(instruments[i].program))
            
        #/media/data/3D/projets/darknet-letters/letters/midi/music/Quizas.mid
        #/media/data/3D/projets/darknet-letters/letters/midi/json/Quizas.json
        l = self.midi_file.split(".")
        name = l[0]
        name = name.replace("music", "json")
        file_name =  name + ".json"
        
        with open(file_name, 'w') as f_out:
            json.dump(json_data, f_out)
    
        print('Enregistrement de:', file_name)

    def get_instruments(self):
        """instruments =
        [Instrument(program=71, is_drum=False, name="mélodie"), ...]
        """

        # Récupération des datas avec pretty_midi
        midi_pretty_format = pretty_midi.PrettyMIDI(self.midi_file)
        self.end_time = midi_pretty_format.get_end_time()
        instruments = midi_pretty_format.instruments

        print("Liste des instruments:")
        for instrument in instruments:
            print("   ", instrument)
        
        return instruments

    def get_instrument_roll(self, partition):
        """Retourne un np.array de (128, FPS*durée du morceau en secondes)"""

        # La méthode get_piano_roll marche pour tous les instruments
        instrument_roll = partition.get_piano_roll(self.FPS,
                                                   np.arange(0,
                                                             self.end_time,
                                                             1/self.FPS))

        return instrument_roll

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
                    velocity = int(ligne[n])
                    if velocity > 127:
                        velocity = 127
                    notes.append((n, velocity))
            partition.append(notes)

        return partition


class AnalyseAndPlay:

    def __init__(self, midi, FPS, fonts):
        """Fichier midi et FPS"""

        self.midi = midi
        self.FPS = FPS
        self.fonts = fonts
        self.partitions = []
        self.analyse_and_play()

    def thread_display(self, disp):
        thread = threading.Thread(target=disp.display)
        thread.start()

    def analyse_and_play(self):
        amf = AnalyseMidiFile(self.midi, self.FPS)
        self.partitions, self.instruments = amf.get_partitions()
        print("Fin de l'analyse des partitions:")
        print("    Nombre de partition", len(self.partitions))

        for i in range(len(self.partitions)):
            # On ne peut utiliser que la bank 0 qui comprend 128 instruments
            bank = 0
            bank_number = self.instruments[i].program
            self.thread_play_partition(bank,
                                       bank_number,
                                       self.partitions[i])

        sleep(len(self.partitions[0])/100)
        print("Fin du fichier", file_list[n])
            
    def play_partition(self, bank, bank_number, partition):
        pomp = PlayOneMidiPartition(self.fonts, bank, bank_number)
        pomp.play_partition(partition, self.FPS)

    def thread_play_partition(self, bank, bank_number, partition):
        """Le thread se termine si note_off"""

        thread = threading.Thread(target=self.play_partition, args=(
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

    def play(self):
        for i in range(len(self.partitions)):
            bank = 0
            bank_number = self.instruments[i]
            partition = self.partitions[i]
            self.thread_play_partition(bank, bank_number, partition)

    def play_partition(self, bank, bank_number, partition):
        """
        bank = 0
        bank_number = instrument[]
        partition = [[(82,100)], [(82,100), (45,88)], [(0,0)], ...
        """
        pomp = PlayOneMidiPartition(self.fonts, bank, bank_number)
        pomp.play_partition(partition, self.FPS)

    def thread_play_partition(self, bank, bank_number, partition):
        """Le thread se termine si note_off"""

        thread = threading.Thread(target=self.play_partition, args=(
                                                                bank,
                                                                bank_number,
                                                                partition))
        thread.start()


if __name__ == '__main__':

    file_list = []
    d = "/media/data/3D/projets/darknet-letters/letters/midi/music"
    for path, subdirs, files in os.walk(d):
        for name in files:
            if name.endswith("mid"):
                file_list.append(str(pathlib.PurePath(path, name)))
    
    # #n = randint(0, len(file_list)-1)
    # #print("\nFichier en cours:", file_list[n])

    # FPS de 10 (trop petit) à 100 (bien)
    FPS = 60

    # Il faut installer FluidR3_GM.sf2
    fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"


    # Création des json
    for midi in file_list:
        amf = AnalyseMidiFile(midi, FPS)
        partitions, instruments = amf.get_partitions()
        amf.save_midi_json(partitions, instruments)

    # #root = "/media/data/3D/projets/darknet-letters/letters/"
    # #midi = root + "midi/music/Out of Africa.mid"
    # #midi_json = root + "midi/json/Out of Africa.json"
    
    # Création d'un json
    # #m = "/media/data/3D/projets/darknet-letters/letters/midi/music/Le grand blond.mid"
    # #amf = AnalyseMidiFile(m, FPS)
    # #partitions, instruments = amf.get_partitions()
    # #amf.save_midi_json(partitions, instruments)
        
    # ## Joue un json
    # #json = "/media/data/3D/projets/darknet-letters/letters/midi/json/Le grand blond.json"
    # #pjm = PlayJsonMidi(json, FPS, fonts)
    # #pjm.play()

    # ## Pour analyser et jouer
    # #midi = file_list[n]
    # #aap = AnalyseAndPlay(midi, FPS, fonts)
