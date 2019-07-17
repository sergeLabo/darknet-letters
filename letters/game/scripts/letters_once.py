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

'''
Ce script est appelé par main_init.main dans blender
Il ne tourne qu'une seule fois pour initier lss variables
qui seront toutes des attributs du bge.logic (gl)
Seuls les attributs de logic sont stockés en permanence.
'''


import os, sys
import json
import threading
import pathlib
from random import randint

from bge import logic as gl

from pymultilame import MyConfig, MyTools, Tempo
from pymultilame import TextureChange, get_all_objects

sys.path.append("/media/data/3D/projets/darknet-letters/letters/midi")
from analyse_play_midi import PlayJsonMidi, PlayOneMidiNote


def get_conf():
    """Récupère la configuration depuis le fichier *.ini."""
    gl.tools =  MyTools()
    
    # Chemin courrant
    abs_path = gl.tools.get_absolute_path(__file__)
    print("Chemin courrant", abs_path)

    # Nom du script
    name = os.path.basename(abs_path)
    print("Nom de ce script:", name)

    # Abs path de semaphore sans / à la fin
    parts = abs_path.split("/letters/")
    print("Recherche de letters:", parts)
    gl.root = os.path.join(parts[0], "letters")
    print("Path de letters: ", gl.root)

    # Dossier *.ini
    ini_file = gl.root + "/global.ini"
    print("Fichier de configuration:", ini_file)
    gl.ma_conf = MyConfig(ini_file)
    gl.conf = gl.ma_conf.conf

    print("\nConfiguration du jeu Darknet Letters:")
    print(gl.conf, "\n")


def set_tempo():

    # Création des objects
    tempo_liste = [("seconde", 60), ("frame", 999999999)]
    gl.tempo = Tempo(tempo_liste)
    gl.frame_rate = 0
    gl.time = 0


def get_midi_json():
    """
    json_data = {"partitions":  [partition_1, partition_2 ......],
                 "instruments": [instrument_1.program,
                                 instrument_2.program, ...]
    """
                  
    # ## TODO chemin à revoir
    # #json_f = "strauss ainsi parla zarathoustra.json"
    # #json_f = "Capri.json"
    # #json_f = "Michael_Jackson_-_Man_In_The_Mirror.json"
    # #json_f = "ABBA_-_Gimme_Gimme_Gimme.json"
    # #json_f = "Video_Game_Themes_-_Final_Fantasy_3.json"
    # #json_f = "Le grand blond.json"
    # #json_f = "Out of Africa.json"
    # #json_f = "Pepito.json"
    # #json_f = "Out of Africa.json"
    # #json_f = "test.json"
    json_f = "Yellow-Submarine.json"
    
    root = "/media/data/3D/projets/darknet-letters/letters/midi/json/"
    gl.midi_json = root + json_f
    print("Fichier midi en cours:", gl.midi_json)

    with open(gl.midi_json) as f:
        data = json.load(f)

        # TODO bizarre la liste data["partitions"] est dans une liste
        gl.partitions = data["partitions"]  # [partition_1, partition_2 ..
        gl.instruments = data["instruments"]  # [instrument_1.program, ...
        gl.partition_nbr = len(gl.partitions)
        print("Nombre d'instrument:", len(gl.instruments),
              "Nombre de partitions:", len(gl.partitions))

                  
def play_json():
    """Play le json"""

    FPS = 50  # TODO
    fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    gl.pjm = PlayJsonMidi(gl.midi_json, FPS, fonts)
    gl.pjm.play()


def init_midi():
    # TODO bordel
    """bank = 0
    bank_number = instrument[]
    Dans PlayOneMidiPartition, une note est jouée avec:
        .thread_note(note, volume)
    La note est stoppée si:
        objet.thread_dict[i] = 0
    """
    
    FPS = 50  # TODO
    fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    bank = 0
    gl.pomn = {}

    channel = 1
    for instrum in gl.instruments:
        bank_number = instrum 
        gl.pomn[instrum] = PlayOneMidiNote(fonts,channel, bank, bank_number)
        channel += 1
        

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
    gl.notes = {}
    gl.obj_name_list_to_display = []

    # Pratique ça
    gl.all_obj = get_all_objects()

    
def main():
    """Lancé une seule fois à la 1ère frame au début du jeu par main_once.
    gl.tc = TextureChange(all_obj["Plane"], "A.png")"""

    print("Initialisation des scripts lancée un seule fois au début du jeu.")

    # Récupération de la configuration
    get_conf()

    set_tempo()

    # midi
    get_midi_json()
    #play_json()
    init_midi()
    
    set_variable()

    # Pour accélérer le jeu, mais ne marche pas
    set_all_letters_unvisible()
    set_all_letters_suspendDynamics()

    # En dehors de la vue caméra
    set_all_letters_position()
    
    # Pour les mondoshawan
    print("\nBonjour des mondoshawans\n\n")
