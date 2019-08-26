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

json_dict = {"partitions": [], "instruments": []}

# Définition d'un drum
instr = [[0, 63], "true", "drum"]
json_dict["instruments"].append(instr)

# Définition des partitions
# a et b compris entre 0 et 127


# Minuscules
part = []
for j in range(10):
    for i in range(30):
        part.append([])
    for i in range(5):
        # note
        a = 80
        # volume
        b = 99
        part.append([[a, b]])

json_dict["partitions"].append(part)

print("\n\nNombre de notes dans la partition:")
print("Partition", i, len(json_dict["partitions"][0]))


# Json
data = json.dumps(json_dict)

f = "drum_test.json"
mode = "w"
tools.write_data_in_file(data, f, mode)
