#!/usr/bin/env python3
# -*- coding: utf8 -*-

########################################################################
# This file is part of Darknet Letters.
#
# Darknet Letters is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Darknet Letters is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
########################################################################


"""
Table des instruments MIDI
    https://www.zikinf.com/articles/mao/tablemidi.php

Installation:
    numpy
    fluidsynth
    FluidR3_GM.sf2
    mido
    
my_pretty_midi est le module pretty_midi modifié pour récupérer les notes
des percussions, mais il ne permet pas d'en avoir les instruments (program).

Les fichiers midi sont dans ... darknet-letters/letters/midi/music/
et peuvent être dans des sous-dossiers

Les json seront dans darknet-letters/letters/midi/json/
"""


import os, sys
from time import sleep
import threading
import json
from random import choice
import numpy as np
from pathlib import Path
import fluidsynth

# Le package (dossier) my_pretty_midi est dans le dossier de ce script
import my_pretty_midi

# Mon package perso
from pymultilame import MyTools


class AnalyseMidi:
    """Analyse le fichier midi,
    trouve le nombre et le nom des instruments.
    Retourne la liste des notes sur une time lapse de chaque instrument.
    save_midi_json enregistre le midi en json

    partitions = liste des partitions
    instruments = liste des instruments soit objet avec .program et .name

    L'enregistrement des json avec chemins absolus ne marche que pour letters

    Sous répertoires et sous sous répertoires possible dans /music
    """

    def __init__(self, midi_file, FPS, volume=""):
        """Un seul fichier midi
        FPS de 10 à 1000, 50 ou 100 est bien
        Plus le FPS est élevé, plus le temps de calcul est long !
        """

        print("\n\nAnalyse de", midi_file.split('/')[-1], "\n")

        self.midi_file = midi_file
        self.FPS = FPS
        self.volume = volume
        
        self.end_time = 0
        self.instruments = None
        self.instruments = []
        self.partitions = []
        self.mytools = MyTools()

        # Pour gérer les threads dans blender
        self.end = 0
        
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
        self.instruments_without_drums = midi_pretty_format.instruments

        # Correction des intruments pour avoir le program des drums
        self.get_instruments_with_drums()

        return self.instruments

    def get_instruments_with_drums(self):
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

        for instrument in self.instruments_without_drums:
            program = instrument.program
            is_drum = instrument.is_drum
            name = instrument.name

            if is_drum:
                bank, bank_nbr = self.get_drum_program()
            else:
                bank = 0
                bank_nbr = int(program)
            self.instruments.append(((bank, bank_nbr), is_drum, name))

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

        drums = [(0, 112),
                 (0, 113),
                 (0, 114),
                 (0, 115),
                 (0, 116),
                 (0, 117),
                 (0, 118),
                 (0, 119),
                 (8, 116),
                 (8, 117),
                 (8, 118)]
        c = choice(drums)
        return c[0], c[1]

    def get_partitions_and_instruments(self):
        """Fait les étapes pour tous les instruments,
        retourne les instruments et leurs partitions.
        """

        # Si fichier midi anormal
        try:
            self.get_instruments()
        except:
            print("Instruments non récupérable dans le fichier midi\n")
            self.instruments_without_drums = []

        # Si nombre d'instrument > 10 pour IA
        if len(self.instruments) > 10:
            return None, None
            
        for instrument in self.instruments_without_drums:
            if instrument.is_drum:
                drum = "Drum"
            else:
                drum = ""
            print("    Analyse de l'instrument: {:>2} {:>6}   Name: {:>24}".\
            format(instrument.program, drum, instrument.name))

            # Array de 128 x nombre de frames
            instrument_roll = self.get_instrument_roll(instrument)

            # Conversion dans une liste de listes python
            partition = self.get_partition(instrument_roll, instrument)
            self.partitions.append(partition)
        print()
        return self.partitions, self.instruments

    def get_partition(self, instrument_roll, instrument):
        """entrée:
        une ligne du array = (0.0 0.0 0.0 ... 89 ... 91 ... 0.0)
                                             89 est à la position 54
                                                    91 est à la position 68
        sortie:
        une ligne de la liste: 2 notes du même instrument 54 et 68
            [(54, 89), (68, 91)] = [(note=54, volume=89), (note=68, volume=91)]
        """

        partition = []
        
        # Parcours de toutes les lignes
        for n in range(instrument_roll.shape[1]):
            # Analyse des lignes pour ne garder que les non nuls
            non_zero = np.flatnonzero(instrument_roll[:,n])
            notes = []
            if non_zero.size > 0:
                note = int(non_zero[0])
                volume = int(instrument_roll[:,n][note])
                if note:
                    notes.append((note, volume))
            partition.append(notes)

        # velocity maxi entre 0 et 127
        partition = normalize_velocity(partition)
        if self.volume == "flat":
            partition = flatten_partition(partition)
        
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
        """Commence par analyser le midi, puis enregistre.
        
        partitions = liste des partitions = [partition_1, partition_2 ...]
        instruments = [Instrument(program=71, is_drum=False, name="mélodie"),
                        ...]

        json_data = {"partitions":  [partition_1, partition_2 ......],
                     "instruments": [instrument_1.program,
                                     instrument_2.program, ...]
                      instrument is not JSON serializable = objet pretty_midi

        midi dans /media/data/3D/projets/darknet-letters/letters/midi/music
                     sous dossiers possible
        json dans /media/data/3D/projets/darknet-letters/letters/midi/json_fps
        et sous dossiers
        """

        # Analyse du midi
        self.get_partitions_and_instruments()

        if len(self.instruments) < 11:
            # Création du json
            json_data = {}
            json_data["partitions"] = self.partitions
            json_data["instruments"] = self.instruments
            
            # Save du json
            json_name = self.get_json_name()
            with open(json_name, 'w') as f_out:
                json.dump(json_data, f_out)
            f_out.close()
            print('Enregistrement de:', json_name)

        # Pour Blender
        self.end = 1

        return self.instruments
        
    def get_json_name(self):
        """Le fichier midi_file est le chemin relatif du fichier dans :
        ./midi/music/
             ou 
        ./midi/music/non_git/

        Le json sera dans le dossier 
        ./midi/json_60/
        ou
        ./midi/json_60/non_git/
        """

        # Remplacement de l'extension .midi en .json
        filename = Path(self.midi_file).with_suffix(".json")
        filename = str(filename)
        
        # Remplacement de music par json
        json_name = filename.replace("music/",
                                     "json_" + str(self.FPS) + "/")

        print("Nom du fichier json", json_name)
        
        # Crée les dossiers et sous dossiers
        self.create_directories(json_name)
        
        return json_name

    def create_directories(self, json_name):
        """
        json_name converti en absolu pour valable ici ou dans blender

        json_name = /med/da/3D/pr/dark/let/midi/json_fps_17/toto.json
                                        5
        json_fps =  /med/da/3D/pr/dark/let/midi/json_fps_17/oui/toto.json
                                                    7
        """

        json_name_abs = Path(json_name).absolute()
        
        # json_17 doit toujours exister, si existe on passe
        index_midi = json_name_abs.parts.index("midi")

        # Bidouille pour agréger les parts
        a = Path(json_name_abs.parts[0])
        b = json_name_abs.parts[1:index_midi + 2]
        json_fps = a.joinpath(*b)
        
        # json_fps = Chemin absolu de json_fps
        self.mytools.create_directory(json_fps)

        # Sous répertoires
        if len(json_name_abs.parts) - index_midi == 4:
            sd_fin = json_name_abs.parts[1:index_midi + 3]
            sd = a.joinpath(*sd_fin)
            print("Sous dossier", sd)
            self.mytools.create_directory(sd)
            
        # Sous sous répertoires
        if len(json_name_abs.parts) - index_midi == 5:
            # Création du sous répertoire
            sd_fin = json_name_abs.parts[1:index_midi + 3]
            sd = a.joinpath(*sd_fin)
            print("Sous dossier", sd)
            self.mytools.create_directory(sd)
            
            # Création des sous sous répertoires
            ssd_fin = json_name_abs.parts[1:index_midi + 4]
            ssd = a.joinpath(*ssd_fin)
            print("Sous sous dossier", ssd)
            self.mytools.create_directory(ssd)

            
class PlayMidi:
    """oip = OneInstrumentPlayer(fonts, channel, bank, bank_number)
    oip.play_note(note, volume)
    Il faut analyser avant de jouer !
    """

    def __init__(self, midi_file, FPS, fonts):

        self.midi_file = midi_file
        self.FPS = FPS
        self.fonts = fonts
        self.partitions = []
        self.end_file = []
        self.instr_nbr = 0
        
        # Analyse et joue au lancement
        self.analyse_and_play()

    def analyse_and_play(self):
        # Objet Analyse du fichier
        am = AnalyseMidi(self.midi_file, self.FPS)

        # Récupération des partitions
        am.get_partitions_and_instruments()
        self.partitions = am.partitions
        self.instr_nbr = len(self.partitions)
        self.instruments = am.instruments
        self.instruments_without_drums = am.instruments_without_drums

        print("Play de", self.midi_file.split('/')[-1], "\n")
        print("    Nombre de partition", len(self.partitions))

        channels = get_channel(self.instruments)

        # Création d'un dict des objets pour jouer chaque instrument
        instruments_player = {}
        for i in range(self.instr_nbr):
            instrument = self.instruments[i]
            chan = channels[i]
            is_drum = instrument[1]
            bank = instrument[0][0]
            bank_number = instrument[0][1]

            if is_drum:
                dr = "Drum"
            else:
                dr = ""
            print('    Channel: {:>2} Bank: {:>1} Number: {:>3} {}'.\
            format(chan, bank, bank_number, dr))
            
            instruments_player[i] = PlayOneMidiPartition(self.partitions[i],
                                                              fonts,
                                                              chan,
                                                              bank,
                                                              bank_number,
                                                              self.FPS)

        # Vérification de la fin
        print()
        while len(self.end_file) < self.instr_nbr:
            for i in range(self.instr_nbr):
                if instruments_player[i].end == 1:
                    if i not in self.end_file:
                        self.end_file.append(i)
            sleep(1)
        print("\nFin du morceau:", self.midi_file.split('/')[-1], "\n")


class PlayOneMidiPartition:
    """Ne fonctionne qu'avec FluidR3_GM.sf2"""

    def __init__(self, partition, fonts, channel, bank, bank_number, FPS):
        """self.channel 1 to 16
        channel 10 pour les drums
        """

        self.partition = partition
        self.fonts = fonts
        self.channel = channel
        self.bank = bank
        self.bank_number = bank_number
        self.FPS = FPS
        self.player = OneInstrumentPlayer(fonts, channel, bank, bank_number)
        self.end = 0

        # Le thread est lancé à la création de l'objet
        self.thread_play_partition()

    def play_note(self, note, volume):
        """Joue la note"""

        if self.player.thread_dict[note] == 0:
            self.player.thread_play_note(note, volume)
            self.player.thread_dict[note] = 1

    def stop_notes(self, note):
        """Stop des notes autres que note."""

        for k in range(128):
            if k != note:
                self.player.thread_dict[k] = 0

    def play_partition(self):
        """partition = liste de listes (note=82, velocity=100)
        [[(82,100)], [(82,100), (45,88)], [(0,0)], ...
        un item tous les 1/FPS
        """

        # Pour un seul instrument, une partition
        for event in self.partition:
            # event sont les notes pour la frame
            if event:
                # event = [[67, 99], [69, 99]]
                # la liste est dans une liste qui peut avoir plusieurs
                # notes d'un même instrument soit un accord,
                # je ne garde que la première note
                note = event[0][0]
                volume = event[0][1]
                # Je joue
                self.play_note(note, volume)
                print(note, volume)
                # Je stope les autres notes que note !
                self.stop_notes(note)
            sleep(1/self.FPS)
        self.stop_partition()

    def stop_partition(self):
        for k in range(128):
            self.player.thread_dict[k] = 0
        self.player.stop_audio()
        #print("Fin de:", self.channel, self.bank, self.bank_number)
        self.end = 1

    def thread_play_partition(self):
        thread_partition = threading.Thread(target=self.play_partition)
        thread_partition.start()


class OneInstrumentPlayer:
    """Un instrument est défini avec fonts, channel, bank, bank_number.

    Ne fonctionne qu'avec FluidR3_GM.sf2
    note et volume entre 0 et 127
    Pas de variation de volume en cours de note,
    une seule note par instrument à la fois.
    """

    def __init__(self, fonts, channel, bank, bank_number, verbose=0):
        """self.channel 1 to 16
        fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
        bank = 0, il y a d'autres bank dans FluidR3_GM.sf2
                    mais pas toujours avec 128 instruments
        bank_number = 0 à 127,
                        idem pas toujours 128 instruments par bank_number

        self.thread_dict = {69: 1, 48: 1, 78:0}
        """

        # 1 objet OneInstrumentPlayer = 1 channel
        self.channel = channel
        self.fonts = fonts
        self.bank = bank
        self.bank_number = bank_number
        self.verbose = verbose
        
        self.set_audio()
        # Le thread
        # #self.thread_note = {}
        # Pour gérer les threads
        self.thread_dict = {}
        # #self.volume = {}
        for i in range(128):
            # Pour gérer les notes
            self.thread_dict[i] = 0

    def set_audio(self):
        """Spécifique à FluidR3_GM.sf2
        note from 0 to 127 but all values are not possible in all bank
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

    def stop_audio(self):
        """Stopper avant de détruire l'objet OneInstrumentPlayer"""

        if self.verbose:
            a = "    Player alsa stoppé: Channel {:>2} Bank {:>1} Number {:>3}"
            print(a.format(self.channel, self.bank, self.bank_number))
            
        self.fs.delete()

    def play_note(self, note, volume):
        """Lancé par le thread thread_play_note
        Se termine si self.thread_dict[note] = 0
        """

        if self.verbose:
            print("Lancement du thread: channel =", self.channel,
                                        "note =", note,
                                        "volume =", volume)

        # Excécution de la note
        self.fs.noteon(self.channel, note, volume)

        # Boucle qui tourne en rond en attendant self.thread_dict[note] = 0
        while self.thread_dict[note]:
            sleep(0.0001)

        # #self.thread_note[note].join()
        
        # Sinon fin de la note
        if self.verbose:
            print("      Fin du thread: channel =", self.channel,
                              "note =", note,
                            "volume =", volume)

        self.fs.noteoff(self.channel, note)

    def thread_play_note(self, note, volume):
        """Le thread se termine si self.thread_dict[(note, volume)]=0
        note et volume entre 0 et 127
        """

        note, volume = cut_the_top_off_note_volume(note, volume)

        # Excécution de la note si elle n'est pas en cours
        if not self.thread_dict[note]:
            self.thread_dict[note] = 1
            thread_note = threading.Thread(target=self.play_note,
                                                args=(note, volume))
            thread_note.start()


class PlayJsonFile:

    def __init__(self, midi_json, FPS, fonts):
        """midi_json créé avec AnalyseMidi"""

        self.midi_json = midi_json
        self.partitions, self.instruments = self.get_data_json(midi_json)
        self.FPS = FPS
        self.fonts = fonts
        self.end_file = []
        self.instr_nbr = len(self.partitions)

    def get_data_json(self, midi_json):
        """
        json_data = {"partitions":  [partition_1, partition_2 ......],
                     "instruments": [instrument_1.program,
                                     instrument_2.program, ...]
        """

        with open(self.midi_json) as f:
            data = json.load(f)
        f.close()
        
        partitions = data["partitions"]
        instruments = data["instruments"]

        return partitions, instruments

    def play(self):
        """Appelée pour jouer le json"""

        print("\nPlay de:", self.midi_json.split("/")[-1])

        channels = get_channel(self.instruments)

        pomp = {}
        for i in range(len(self.partitions)):
            # [[0, 117], true, "Drums2"]
            chan = channels[i]
            is_drum = self.instruments[i][1]
            bank = self.instruments[i][0][0]
            bank_number = self.instruments[i][0][1]
            partition = self.partitions[i]
            print('    Channel: {:>2} Bank: {:>1} Number: {:>3} Drum: {:>1}'.\
            format(chan, bank, bank_number, is_drum))
        
            pomp[i] = PlayOneMidiPartition(partition,
                                           self.fonts,
                                           chan,
                                           bank,
                                           bank_number,
                                           self.FPS)

        # Vérification de la fin
        while len(self.end_file) < self.instr_nbr:
            for i in range(self.instr_nbr):
                if i in pomp:
                    if pomp[i].end == 1:
                        if i not in self.end_file:
                            self.end_file.append(i)
            sleep(0.01)
        # Je kill
        del pomp
        
        print("\nFin du morceau:", self.midi_json.split("/")[-1])

        
def get_channel(instruments):
    """16 channel maxi
    Drums
        channel 9 si on compte de 0
        et 10 si on compte de 1
    Les channels sont attribués dans l'ordre des instruments de la liste
    """

    channels = []
    channels_no_drum = [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16]
    nbr = 0
    for instrument in instruments:
        if not instrument[1]:  # instrument[1] = boolean
            if nbr >= 15: nbr = 0
            channels.append(channels_no_drum[nbr])
            nbr += 1
        else:
            channels.append(10)
    return channels

        
def normalize_velocity(partition):
    """partition[0] = [[couple], [couple]]"""

    # Recherche du volume maxi
    volume_maxi = 0
    for couple in partition:
        if couple:
            if couple[0][1] > volume_maxi:
                volume_maxi = couple[0][1]

    print("    Volume maxi =", volume_maxi)

    # Correction du volume
    if volume_maxi > 127:
        print("    Correction du volume de l'instrument")
        for c in range(len(partition)):
            if partition[c]:
                note = partition[c][0][0]
                volume = partition[c][0][1]
                correct = int((volume * 127) / volume_maxi)
                partition[c] = [(note, correct)]

    return partition


def flatten_partition(partition):
    """Set les volume=velocity à 127"""
    
    print("Volume de la partition à 127")
    for c in range(len(partition)):
        if partition[c]:
            note = partition[c][0][0]
            volume = 127
            partition[c] = [(note, volume)]
            
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
                    file_list.append(str(Path(path, name)))

    return file_list


def midi_file_list_in_music_dir():
    """Retourne la liste des fichiers mid et midi dans /music et
    sous répertoires
    """

    directory = "./music"
    extentions = [".midi", "mid", "kar", "Mid", "MID"]

    return get_file_list(directory, extentions)


def json_file_list_in_json_dir():
    """Retourne la liste des fichiers mid et midi dans /music et
    sous répertoires
    """

    directory = "./json"
    extentions = [".json"]

    return get_file_list(directory, extentions)


def create_all_json(directory, FPS, volume):
    """Création des json des fichiers midi de file_list"""

    # Création des json
    extentions = [".midi", "mid", "kar", "Mid", "MID"]
    file_list = get_file_list(directory, extentions)
    print("Nombre de fichiers midi à analyser:", len(file_list))
    all_instruments = {}
    for midi in file_list:
        instruments = create_one_json(midi, FPS, volume)
        all_instruments[midi] = instruments

    save_all_instruments(all_instruments, FPS)


def save_all_instruments(all_instruments, FPS):
    """dans ./all_instruments"""
    
    # Save du json
    json_name = "./all_instruments/all_instruments_" + str(FPS) + ".json"
    with open(json_name, 'w') as f_out:
        json.dump(all_instruments, f_out)
    f_out.close()

    
def create_one_json(midi_file, FPS, volume):
    """Création d'un json"""

    am = AnalyseMidi(midi_file, FPS, volume)
    instruments = am.save_midi_json()
    
    return instruments


def play_all_json(directory, FPS, fonts):
    """Joue tous les json du dossier json"""

    extentions = [".json"]
    file_list = get_file_list(directory, extentions)
    print("Nombre de fichiers json:", len(file_list))
    for i in range(len(file_list)):
        json_file = file_list[i]
        pjm = PlayJsonFile(json_file, FPS, fonts)
        pjm.play()
        del pjm


def analyse_play_one_midi(midi_file, FPS, fonts):
    """Pour analyser et jouer"""

    pm = PlayMidi(midi_file, FPS, fonts)


def play_all_midi_files(FPS, fonts):
    midi_list = get_file_list("./music/pas_pour_github", ['mid'])
    for m in midi_list:
        PlayMidi(m, FPS, fonts)

        
if __name__ == '__main__':
    """Le nombre d'instruments est limité à 10 !!!
    Les threads dans blender ne sont plus utilisés !
    """
    
    # #midi_file = "..midi/music/non_git/jeux_interdits.mid"
    # #create_one_json(midi_file, 60, "")
    
    # ## Création de tous les json à FPS 60 pour blender display
    # #FPS = 60
    # #volume = ""
    # #create_all_json("./music/", FPS, volume)

    # Création des json pour test de l'IA
    # Pour forcer le volume pour l'IA bête
    # Set le volume à 127 partout dans les json
    FPS = 40
    # #volume = "flat"
    # #create_all_json("./music/non_git/ia", FPS, volume)

    # #fonts = "./soundfont/TimGM6mb.sf2"
    # #fonts = "./soundfont/merlin_vienna.sf2"
    # #fonts = "./soundfont/MuseScore_General.sf3"
    fonts = "./soundfont/MuseScore_General_Full.sf2"
    # #fonts = "./soundfont/FluidR3_GM.sf2"
    # #fonts = "./soundfont/percussion/142-Cymbal Roll.sf2"
    
    # ## Analyse et play d'une music
    # #midi_file = "./music/pas_pour_github/Capri.mid"
    # #analyse_play_one_midi(midi_file, FPS, fonts)

    # Play un midi
    # #mf = "axel_f-crazy_frog.mid"
    # #midi_file = "./music/pas_pour_github/" + mf
    # #PlayMidi(midi_file, FPS, fonts)

    # ## Play de tous les midi
    # #play_all_midi_files(FPS, fonts)
            
    # ## Joue les json
    # #play_all_json("../midi/json_40/non_git/ia", FPS, fonts)

    # ## Création d'un json pour to_image
    # #f = "./music/pas_pour_github/axel_f-crazy_frog.mid"
    # #am = AnalyseMidi(f, 17)
    # #am.save_midi_json()
    
    # Play un json
    json_file = "../midi/json_40/non_git/ia/gaynor_i_will_survive.json"
    pjm = PlayJsonFile(json_file, 40, fonts)
    pjm.play()
    del pjm
