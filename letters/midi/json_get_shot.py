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

# Nombre de shot à réaliser
nbr = CONF["blend"]["total"]

loop = int(sqrt(nbr)+1)
print("Nombre de boucle à réaliser", loop)
# os._exit(0)

# Le couteau
tools = MyTools()

json_dict = {"partitions": [], "instruments": []}

# Définition des instruments
for i in range(10):
    instr = [[0, 2*i], "false", " "]
    json_dict["instruments"].append(instr)

# Définition des partitions
# a et b compris entre 0 et 127

# Minuscules
for partition in range(10):
    part = []
    for i in range(loop):
        for j in range(loop):
            if j % 2 == 0:
                # note
                a = randint(0, 127)
                # volume
                b = 0
            else:
                # note
                a = 0
                # volume
                b = randint(0, 127)
            print(a, b)
            part.append([[a, b]])
            
    json_dict["partitions"].append(part)

print("\n\nNombre de notes par partition:")
for i in range(10):
    print("Partition", i, len(json_dict["partitions"][0]))
    
print("\n\nNombre de notes en trop:", loop*loop - nbr)


# Json
data = json.dumps(json_dict)

f = "get_shot.json"
mode = "w"
tools.write_data_in_file(data, f, mode)
