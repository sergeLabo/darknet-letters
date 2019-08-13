#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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
Ce script est appelé par main_init.main dans blender
Il ne tourne qu'une seule fois pour initier les variables
qui seront toutes des attributs du bge.logic (gl)
Seuls les attributs de logic sont stockés en permanence.

Il est relancé par main de letters_always à la fin du morceau.

suspendDynamics(False) 
"""


import os, sys
from time import sleep
import json
from pathlib import Path
import random

from bge import logic as gl
from bge import render

from pymultilame import MyConfig, MyTools, Tempo
from pymultilame import TextureChange, get_all_objects

# Ajout du dossier courant dans lequel se trouve le dossier my_pretty_midi
CUR_DIR = Path.cwd()
print("Chemin du dossier courant dans le BGE:", CUR_DIR.resolve())  # game

# Chemin du dossier letters
LETTERS_DIR = CUR_DIR.parent
sys.path.append(str(LETTERS_DIR) + "/midi")

# analyse_play_midi est dans /midi
from analyse_play_midi import PlayJsonMidi, OneInstrumentPlayer


# Pour retrouver le début du jeu dans le terminal
print("\n"*20)


def get_conf():
    """Récupère la configuration depuis le fichier *.ini."""
    gl.tools =  MyTools()

    gl.letters_dir = str(LETTERS_DIR.resolve())
    
    # Dossier *.ini
    ini_file = gl.letters_dir + "/global.ini"
    gl.ma_conf = MyConfig(ini_file)
    gl.conf = gl.ma_conf.conf

    print("\nConfiguration du jeu Darknet Letters:")
    print(gl.conf, "\n")


def set_tempo():

    # Création des objects
    tempo_liste = [ ("seconde", 60),
                    ("frame", 999999999),
                    ("shot", int(gl.conf['blend']['shot_every'])),
                    ("info", 180)]
                    
    gl.tempo = Tempo(tempo_liste)
    gl.frame_rate = 0
    gl.time = 0


def set_all_letters_position():
    """Etalement des lettres name = k"""
    
    l = "abcdefghijklmnopqrstABCDEFGHIJKLMNOPQRST"
    letters = list(l)
    
    for k, v in gl.all_obj.items():
        if "font" in k:
            # font_0_a
            x = 25 + int(k[5])
            # index ok
            y = letters.index(k[7]) 
            v.position = x, y, 0
    

def set_variable():

    # Musique
    gl.frame = 0
    gl.notes = {}
    gl.obj_name_list_to_display = []
    gl.partitions = []
    gl.instruments = []
    
    # Tous les objets
    gl.all_obj = get_all_objects()
    gl.info = ""
    gl.info_news = 0
    gl.all_obj["Text_info"]["Text"] = gl.info

    # nombre de shot total
    gl.nombre_shot_total = gl.conf['blend']['total']
    gl.previous_datas = ""

    # Numero conservé au changement de morceau
    gl.numero = gl.conf['blend']['numero']
    gl.total = gl.conf['blend']['total']
    if gl.numero >= gl.total:
        gl.numero = gl.total
    
    # Dimension des fenêtres
    gl.music_size = gl.conf["blend"]["music_size"]
    gl.shot_size = gl.conf["darknet"]["shot_size"]


def create_directories():
    """Création de 100 dossiers."""

    # Dossier d'enregistrement des images
    gl.shot_directory = gl.conf['blend']["shot_dir"]
    
    # Création du dossier si n'existe pas
    gl.tools.create_directory(gl.shot_directory)
    
    print("Dossier des shots:", gl.shot_directory)

    # Si le dossier n'existe pas, je le crée
    gl.tools.create_directory(gl.shot_directory)

    # Un dossier réparti dans 100 sous dossiers
    for l in range(100):
        directory = os.path.join(gl.shot_directory, str(l))
        gl.tools.create_directory(directory)


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


def get_get_shot_json():

    gl.midi_json = "/media/data/3D/projets/darknet-letters/letters/midi/get_shot.json"
    
    with open(gl.midi_json) as f:
        data = json.load(f)

    gl.partitions = data["partitions"]  # [partition_1, partition_2 ..
    gl.instruments = data["instruments"]  # [instrument_1.program, ...
    gl.partition_nbr = len(gl.partitions)
    
    print("Nombre d'instrument:", gl.partition_nbr)
    print("Nombre de frame:", len(gl.partitions[0]))
    
    
def get_midi_json():
    """
    json_data = {"partitions":  [partition_1, partition_2 ......],
                 "instruments": [instrument_1.program,
                                 instrument_2.program, ...]
    """
                  
    
    gl.nbr = gl.conf["midi"]["file_nbr"]
    js = gl.letters_dir + "/midi/json"
    all_json = gl.tools.get_all_files_list(js, ".json")

    # Reset de gl.nbr si fini
    if gl.nbr >= len(all_json):
        gl.nbr = 0

    # Enregistrement du numéro du prochain fichier à lire
    gl.ma_conf.save_config("midi", "file_nbr", gl.nbr + 1)

    gl.midi_json = all_json[gl.nbr]
    
    print("Fichier midi en cours:", gl.midi_json)

    with open(gl.midi_json) as f:
        data = json.load(f)

    gl.partitions = data["partitions"]  # [partition_1, partition_2 ..
    gl.instruments = data["instruments"]  # [instrument_1.program, ...
    gl.partition_nbr = len(gl.partitions)
    
    # Pour choix 2 et 3
    fonts_shuffle()
    
    print("Nombre d'instrument:", len(gl.instruments))
    

def fonts_shuffle():
    """Le désordre des polices permet de rendre aléatoire
    le choix de la police pour chaque instrument.
    liste en désordre = [9, 5, 1, 4 ...] 10 items
    gl.fonts_dict = {numéro de piste soit 0 à nombre d'instruments:
                        police assignée}
    """

    L = [*range(10)]
    random.shuffle(L)

    gl.fonts_dict = {}
    n = gl.partition_nbr
    if n >= 10: n = 10
    for i in range(n):
        gl.fonts_dict[i] = L[i]
    print("Dict des polices:", gl.fonts_dict)


def get_channel():
    """16 channel maxi
    channel 9 pour drums
    Les channels sont attribués dans l'ordre des instruments de la liste
    """
    
    channels = []
    channels_no_drum = [1,2,3,4,5,6,7,8,10,11,12,13,14,15,16]
    nbr = 0
    for instrument in gl.instruments:
        if not instrument[1]:  # instrument[1] = boolean
            channels.append(channels_no_drum[nbr])
            nbr += 1
            if nbr > 14: nbr = 0
        else:
            channels.append(9)
            
    return channels

                    
def init_midi():
    """bank = 0
    bank_number = instrument[]
    Dans PlayOneMidiPartition, une note est jouée avec:
        .thread_play_note(note, volume)
    La note est stoppée si:
        objet.thread_dict[(note, volume)] = 0

    gl.instruments = [[[0, 25], false, "Bass"], [[0, 116], true, "Drums2"]]
        instrum = [[0, 25], false, "Bass"]
    """
    
    fonts = gl.conf["midi"]["fonts"]
    channels = get_channel()

    # TODO provoque erreur de segmentation
    # ## Pour être sûr que les audio initiés soit bien stoppé
    # #for i in range(10):
        # #try:
            # ## Stop des fluidsynth.Synth() initiés
            # #gl.instruments_player[i].stop_audio()
        # #except:
            # #print("Erreur dans stop des fluidsynth.Synth()")
        
    # Création d'un dict des objets pour jouer chaque instrument
    gl.instruments_player = {}

    # Limitation du nombre d'instruments
    n = len(gl.instruments)
    if n > 10: n = 10
    for i in range(n):
        instrum = gl.instruments[i]
        chan = channels[i]
        is_drum = instrum[1]
        bank = instrum[0][0]
        bank_number = instrum[0][1]
        print("Instrument:", chan, bank, bank_number)  
        gl.instruments_player[i] = OneInstrumentPlayer(fonts, chan, bank,
                                                       bank_number)
        

def intro_init():
    # Phases du jeu "intro" "music and letters" "get shot"
    gl.phase = "intro"


def music_and_letters_init():
    get_conf()
    get_midi_json()
    sleep(0.1)
    init_midi()
    gl.phase = "music and letters"

        
def get_shot_init():
    create_directories()
    get_get_shot_json()
    # Pas de shuffle des polices, elles y passent toutes
    gl.fonts_dict = {}
    for i in range(10):
        gl.fonts_dict[i] = i
    gl.phase = "get shot"

    
def convert_to_json_init():
    """Pour créer les json, 
    """
    gl.FPS = gl.conf["midi"]["fps"]
    gl.json_file_nbr = 0

    midi = gl.letters_dir + "/midi/music"
    extentions = [".midi", "mid", "kar", "Mid", "MID"]
    gl.all_midi_files = get_file_list(midi, extentions)
    print("Nombre de fichiers à convertir:", len(gl.all_midi_files))
    
    # #print("Liste des fichiers midi:")
    # #print("    ", gl.all_midi_files)
    
    # Pour la fin de la conversion
    gl.convert_to_json_end = 1
    gl.conversion = None

    
def main():
    """Lancé une seule fois à la 1ère frame au début du jeu par main_once."""

    print("Initialisation des scripts lancée un seule fois au début du jeu:")

    # Le couteau suisse
    gl.tools = MyTools()
    
    # Récupération de la configuration
    get_conf()
    set_variable()
    set_tempo()        

    # Carrés en dehors de la vue caméra
    set_all_letters_position()

    intro_init()
    
    # Pour les mondoshawan
    print("Initialisation du jeu terminée\n\n")
