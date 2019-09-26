#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
p = {
"partitions": [[[[74, 109]], [[74, 109]], [[74, 109]], [[74, 109]]],
                [[[1, 127]], [[1, 127]], [[1, 127]], [[1, 127]]]],

"instruments": [[[0, 0], false, " "]]
    }

10 parttions
1 partition
[[1,1], [1,2],  ... [1, 127],
[2,1]
...
...
[127,1], ...........[127,127]]

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
loop = int(nbr/(254)) + 1
print("Nombre de boucle à réaliser", loop)

json_dict = {"partitions": [], "instruments": []}

# Définition des instruments
for i in range(10):
    instr = [[0, 0], "false", " "]
    json_dict["instruments"].append(instr)

# 5 partitions
for p in range(5):
    print(p)
    partition = []
    for repeat in range(loop):
        # Minuscules
        for i in range(1, 128):
            partition.append([[i, 0]])
        # Puis majuscules
        for j in range(1, 128):
            partition.append([[0, j]])
        # ## Puis vide
        # #for i in range(1, 256):
            # #partition.append([])
            
    # Ajout d'une partition
    json_dict["partitions"].append(partition)
    
# 5 partitions
for p in range(5, 10):
    print(p)
    partition = []
    for repeat in range(loop):
        # ## Vide
        # #for i in range(1, 256):
            # #partition.append([])
        # Puis minuscules
        for i in range(1, 128):
            partition.append([[i, 0]])
        # Puis majuscules
        for j in range(1, 128):
            partition.append([[0, j]])
                        
    # Ajout d'une partition
    json_dict["partitions"].append(partition)

    
print("\n\nNombre de notes par partition:")
for i in range(10):
    print("Partition", i, len(json_dict["partitions"][i]))

# Json
data = json.dumps(json_dict)
# Fin de ligne à la fin pour github
data += "\n"

f = "get_shot.json"
mode = "w"
tools.write_data_in_file(data, f, mode)


# ## Définition des partitions
# ## a et b compris entre 0 et 127
# #for partition in range(1):
    # #part = []
    # #for i in range(loop):  # 224 pour 50 000
        # #for j in range(loop):
            # ## Moins de lettres donc moins de supperposition
            # ## Minuscules seules
            # #if j % 2 == 0:
                # ## note
                # #a = randint(0, 127)
                # ## volume
                # #b = 0
            # ## Majuscules seules
            # #else:
                # ## note
                # #a = 0
                # ## volume
                # #b = randint(0, 127)
            # #part.append([[a, b]])
    # #json_dict["partitions"].append(part)
