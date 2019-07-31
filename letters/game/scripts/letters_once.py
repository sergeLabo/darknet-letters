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
"""


import os, sys
import json
from pathlib import Path
import random

from bge import logic as gl

from pymultilame import MyConfig, MyTools, Tempo
from pymultilame import TextureChange, get_all_objects

# Ajout du dossier courant dans lequel se trouve le dossier my_pretty_midi
CUR_DIR = Path.cwd()

# Pour retrouver le début du jeu dans le terminal
print("\n"*20)

print("Chemin du dossier courant dans le BGE:", CUR_DIR.resolve())  # game

# Chemin du dossier letters
LETTERS_DIR = CUR_DIR.parent
sys.path.append(str(LETTERS_DIR) + "/midi")

# analyse_play_midi est dans /midi
from analyse_play_midi import PlayJsonMidi, OneInstrumentPlayer


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
                    ("shot", int(gl.conf['blend']['shot_every']))]
                    
    gl.tempo = Tempo(tempo_liste)
    gl.frame_rate = 0
    gl.time = 0
    
    
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
    partitions_shuffle()
    print("Nombre d'instrument:", len(gl.instruments))
    

def partitions_shuffle():
    """Le désordre des partitions (et instruments) permet de rendre aléatoire
    le choix des polices pour chaque instrument
    """
    
    L = [*range(gl.partition_nbr)]
    random.shuffle(L)
    print("Liste en désordre:", L)
    
    partitions_new = list(range(gl.partition_nbr))
    instruments_new = list(range(gl.partition_nbr))
    for i in range(len(L)):
        partitions_new[i]  = gl.partitions[L[i]]
        instruments_new[i] = gl.instruments[L[i]]
        
    gl.partitions  = partitions_new
    gl.instruments = instruments_new
    

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
    
    FPS = gl.conf["midi"]["fps"]
    fonts = gl.conf["midi"]["fonts"]
    channels = get_channel()

    # Création d'un dict des objets pour jouer chaque instrument
    gl.instruments_player = {}
    for i in range(len(gl.instruments)):
        instrum = gl.instruments[i]
        chan = channels[i]
        is_drum = instrum[1]
        bank = instrum[0][0]
        bank_number = instrum[0][1]
        print("Instrument:", chan, bank, bank_number)  
        gl.instruments_player[i] = OneInstrumentPlayer(fonts, chan, bank, bank_number)
        

def set_all_letters_unvisible():
    """Toutes les lettres sont invisible au départ"""
    for k, v in gl.all_obj.items():
        if "font" in k:
            v.visible = False

        
def set_all_letters_suspendDynamics():
    """Toutes les lettres sont sans Dynamics au départ"""
    
    for k, v in gl.all_obj.items():
        if "font" in k:
            v.suspendDynamics(False)


def set_all_letters_position():
    """Etalement des lettres name = k"""
    
    l = "abcdefghijklmnopqrstABCDEFGHIJKLMNOPQRST"
    letters = list(l)
    
    for k, v in gl.all_obj.items():
        if "font" in k:
            # font_0_a
            x = 25 + int(k[5])
            y = letters.index(k[7]) 
            v.position = x, y, 0
    

def set_variable():
    # Phases du jeu
    gl.phase = "get shot"

    # Musique
    gl.frame = 0
    gl.notes = {}
    gl.obj_name_list_to_display = []
    
    # Tous les objets
    gl.all_obj = get_all_objects()
    gl.all_obj["Text_info"]["Text"] = ""

    # nombre de shot total
    gl.nombre_shot_total = gl.conf['blend']['total']
    gl.sleep = gl.conf['blend']['sleep']
    gl.previous_datas = ""

    # Numero conservé au changement de morceau
    gl.numero = gl.conf['blend']['numero']
    gl.total = gl.conf['blend']['total']
    
    
def create_directories():
    """
    Création de n dossiers
    /media/data/3D/projets/semaphore_blend_yolo/shot/a/shot_0_a.png
    """

    # Dossier d'enregistrement des images
    gl.shot_directory = os.path.join(gl.letters_dir, 'shot')
    print("Dossier des shots:", gl.shot_directory)

    # Si le dossier n'existe pas, je le crée
    gl.tools.create_directory(gl.shot_directory)

    # Un dossier réparti dans 100 sous dossiers
    for l in range(100):
        directory = os.path.join(gl.shot_directory, str(l))
        gl.tools.create_directory(directory)

        
def main():
    """Lancé une seule fois à la 1ère frame au début du jeu par main_once."""

    print("Initialisation des scripts lancée un seule fois au début du jeu:")
    
    # Récupération de la configuration
    get_conf()

    set_variable()
    create_directories()
    set_tempo()

    # midi
    get_midi_json()
    if gl.numero == gl.conf['midi']['sound']:
        init_midi()

    # En dehors de la vue caméra
    set_all_letters_position()
    
    # Pour les mondoshawan
    print("Initialisation du jeu terminée\n\n")
