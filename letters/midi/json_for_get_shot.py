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
from pymultilame import MyTools
from  analyse_play_midi import PlayJsonMidi
from random import randint

tools = MyTools()

json_dict = {"partitions": [], "instruments": []}

# Définition des instruments
for i in range(10):
    instr = [[0, 2*i], "false", " "]
    json_dict["instruments"].append(instr)

# Définition des partitions
# a et b compris entre 0 et 127
for partition in range(10):
    part = []
    for i in range(1, 250):
        for j in range(1, 250):
            # note
            # a = (i + partition) % 128
            a = randint(0, 127)
            
            # volume
            # b = (j + partition) % 128
            b = randint(0, 127)
            
            print(a, b)
            
            part.append([[a, b]])
    json_dict["partitions"].append(part)
        
print("Nombre de notes par partition", len(json_dict["partitions"][0]))

# Json
data = json.dumps(json_dict)

f = "get_shot.json"
fichier = "/media/data/3D/projets/darknet-letters/letters/midi/json/"
mode = "w"
tools.write_data_in_file(data, fichier + f, mode)


# #FPS = 60
# #fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
# #root = "/media/data/3D/projets/darknet-letters/letters"
# ## Joue le json
# #json_file = fichier + f
# #pjm = PlayJsonMidi(json_file, FPS, fonts)
# #pjm.play()
