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


import os


from bge import logic as gl

from pymultilame import MyConfig, MyTools, Tempo
from pymultilame import TextureChange, get_all_objects

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
    parts = abs_path.split("/darknet-letters/")
    print("Recherche de darknet-letters:", parts)
    gl.root = os.path.join(parts[0], "darknet-letters")
    print("Path de :darknet-letters", gl.root)

    # Dossier *.ini
    ini_file = os.path.join(gl.root, "global.ini")
    gl.ma_conf = MyConfig(ini_file)
    gl.conf = gl.ma_conf.conf

    print("\nConfiguration du jeu Darknet Letters:")
    print(gl.conf, "\n")


def set_tempo():

    # Création des objects
    tempo_liste = [("test", 60)]
    gl.tempo = Tempo(tempo_liste)

    
def main():
    '''Lancé une seule fois à la 1ère frame au début du jeu par main_once.'''

    print("Initialisation des scripts lancée un seule fois au début du jeu.")

    # Récupération de la configuration
    get_conf()

    set_tempo()

    all_obj = get_all_objects()
    gl.tc = TextureChange(all_obj["Plane"], "A.png")
    
    # Pour les mondoshawan
    print("Bonjour des mondoshawans\n")
