#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
{"partitions": [] voir pls bas

"instruments": [[[0, 0], "false", " "], [[0, 0], "false", " "], [[0, 0],
"false", " "], [[0, 0], "false", " "], [[0, 0], "false", " "], [[0, 0],
"false", " "], [[0, 0], "false", " "], [[0, 0], "false", " "], [[0, 0],
"false", " "], [[0, 0], "false", " "]]}
"""

import os, sys
import json
from math import sqrt
from random import randint

from pymultilame import MyTools

# Import du dossier parent soit letters
# Pas d'import possible direct du dossier parent
# ValueError: attempted relative import beyond top-level package
sys.path.append("..")
from letters_path import LettersPath

lp = LettersPath()
letters_dir = lp.letters_dir
CONF = lp.conf

# Le couteau
tools = MyTools()

# Nombre de shot à réaliser
nbr = CONF["blend"]["total"]
loop = int(nbr/115) + 1
print("Nombre de boucle à réaliser", loop)

json_dict = {"partitions": [], "instruments": []}

# Définition des instruments
for i in range(10):
    instr = [[0, 0], "false", " "]
    json_dict["instruments"].append(instr)

# Liste des possibles
# 19 valeurs * maj et min * 10 = 380 objets
#    b  c  d  e  f  g  h  i  j  k   l   m   n   o   p   q   r   s   t
l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# Minuscule pour la note
# [l[i], 0]
# Majuscule pour le volume
# [0, l[i]]

"""
[[[1, 0]], [[2, 0]], [[3, 0]], [[4, 0]], [[5, 0]], [[6, 0]], [[7, 0]],
[[8, 0]], [[9, 0]], [[10, 0]], [[20, 0]], [[30, 0]], [[40, 0]], [[50, 0]],
[[60, 0]], [[70, 0]], [[80, 0]], [[90, 0]], [[100, 0]], [[0, 1]], [[0, 2]],
[[0, 3]], [[0, 4]], [[0, 5]], [[0, 6]], [[0, 7]], [[0, 8]], [[0, 9]],
[[0, 10]], [[0, 20]], [[0, 30]], [[0, 40]], [[0, 50]], [[0, 60]], [[0, 70]],
[[0, 80]], [[0, 90]], [[0, 100]]]
"""

# Les 10 canaux
partitions = []

# 10 canaux
for n in range(10):
    # La partition du canal
    part = []
    # Boucle pour arriver aux nombre de shot à faire
    for rep in range(loop):
        # Répétition pour avoir une frame vide toutes les 114
        for w in range(3):
            # Minuscules
            for i in range(len(l)):
                note, volume = l[i], 0
                note_vol = [[note, volume]]
                part.append(note_vol)

            # Majuscules
            for i in range(len(l)):
                note, volume = 0, l[i]
                note_vol = [[note, volume]]
                part.append(note_vol)

        # Frame sans note tous les 114 (notes, volumes)
        part.append([])

    partitions.append(part)
    
# Ajout au dict
json_dict["partitions"] = partitions

print("\n\nNombre de notes par partition:")
for j in range(10):
    print("    Partition =", j, "nombre:", len(json_dict["partitions"][j]))

# Json
data = json.dumps(json_dict)
# Fin de ligne à la fin pour github
data += "\n"

f = "get_shot.json"
mode = "w"
tools.write_data_in_file(data, f, mode)
