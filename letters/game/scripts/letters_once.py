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
    tempo_liste = [("test", 60), ("frame", 999999999)]
    gl.tempo = Tempo(tempo_liste)


def get_midi_json():
    """{"Lead Strings": [[[67, 64]], [[67, 64]], [[67, 64]], [[67, 64]], ...

    gl.data = {0: [[52, 63], [46, 47], ...], 0: .....}
    gl.instruments = {0: "Lead Strings", 1: ...}
    """

    root = "/media/data/3D/projets/darknet-letters/letters/midi/"
    gl.midi_json = root + "Yellow-Submarine.json"
    #gl.midi_json = root + "Out of Africa.json"
    with open(gl.midi_json) as f:
        data = json.load(f)

    # Remplacement du nom de l'instrument par numéro
    gl.data = {}
    gl.instruments = {}
    i = 0
    for k, v in data.items():
        gl.data[i] = v
        gl.instruments[i] = k
        i += 1
    gl.partition_nbr = len(gl.data)


def play_json():
    """Play le json"""

    FPS = 50
    fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    bank_GM_txt = "/media/data/3D/projets/darknet-letters/letters/midi/bank_GM.txt"
    gl.pjm = PlayJsonMidi(gl.midi_json, FPS, fonts, bank_GM_txt)
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

    for i in range(5):  # nombre de font min et maj
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
