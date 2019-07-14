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
from analyse_play_midi import PlayJsonMidi


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

    
def get_midi_json_test():
    """
    json_data = {"partitions":  [partition_1, partition_2 ......],
                 "instruments": [instrument_1.program,
                                 instrument_2.program, ...]
    """

    # TODO à revoir
    file_list = []
    d = "/media/data/3D/projets/darknet-letters/letters/midi/json"
    for path, subdirs, files in os.walk(d):
        for name in files:
            if name.endswith("json"):
                file_list.append(str(pathlib.PurePath(path, name)))

    for midi_json in file_list:
        print(midi_json)
        with open(midi_json) as f:
            data = json.load(f)

            # TODO bizarre la liste data["partitions"] est dans une liste
            gl.partitions = data["partitions"]  # [partition_1, partition_2 ..
            gl.instruments = data["instruments"]  # [instrument_1.program, ...
            gl.partition_nbr = len(gl.partitions)
            print("Nombre d'instrument:", len(gl.instruments),
                  "Nombre de partitions:", len(gl.partitions))


def get_midi_json():
    """
    json_data = {"partitions":  [partition_1, partition_2 ......],
                 "instruments": [instrument_1.program,
                                 instrument_2.program, ...]
    """
                  
    # ## TODO chemin à revoir
    json_f = "strauss ainsi parla zarathoustra.json"
    json_f = "Capri.json"
    json_f = "Michael_Jackson_-_Man_In_The_Mirror.json"
    json_f = "ABBA_-_Gimme_Gimme_Gimme.json"
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

    FPS = 50
    fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    gl.pjm = PlayJsonMidi(gl.midi_json, FPS, fonts)
    thread_play_json()


def thread_play_json():
    thread = threading.Thread(target=gl.pjm.play)
    thread.start()


def get_all_lettres():
    """obj_dict = {
    0: "a": nom_de_l_objet_blender = "font_0_a",
    1: ...
    appel du nom d'un objet avec obj_dict[0]["a"]
    """

    m = "abcdefghijklmnopqrst"
    M = "ABCDEFGHIJKLMNOPQRST"
    minus = list(m)
    majus = list(M)
    
    obj_dict = {}

    for i in range(10):  # nombre de font min et maj
        obj_dict[i] = {}
        for l in minus:
            obj_dict[i][l] = "font_" + str(i) + "_" + l 
        for l in majus:
            obj_dict[i][l] = "font_" + str(i) + "_" + l

        
    gl.obj_dict = obj_dict
    

def set_variable():
    gl.notes = {}
    gl.obj_name_list_to_display = []

    
def main():
    """Lancé une seule fois à la 1ère frame au début du jeu par main_once.
    gl.tc = TextureChange(all_obj["Plane"], "A.png")"""

    print("Initialisation des scripts lancée un seule fois au début du jeu.")

    # Récupération de la configuration
    get_conf()

    set_tempo()

    # Le dict avec le nom des objets
    get_all_lettres()

    # midi
    get_midi_json()
    play_json()
    
    set_variable()
    
    # Pour les mondoshawan
    print("\nBonjour des mondoshawans\n\n")
