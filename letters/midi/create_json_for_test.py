#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
p = {
"partitions": [[[[74, 109]], [[74, 109]], [[74, 109]], [[74, 109]]],
                [[[1, 127]], [[1, 127]], [[1, 127]], [[1, 127]]]],

"instruments": [
                [0, # bank_number=numéro d'instrument
                 "false", # is_drum
                 0], # rien si is_drum=false
                [117, # bank_number=numéro d'instrument
                "true", # is_drum
                8] # bank si is_drum=true
                ]
    }
"""

import os, sys
import json
import pathlib
from pymultilame import MyTools
from  analyse_play_midi import play_json


tools = MyTools()

part = {"partitions": [], "instruments": []}

# Définition des instruments
for instr in [[0, "false"], [117, "true"]]: 
    part["instruments"].append(instr)

# Définition des partitions

part_1 = []
for i in range(10):
    # note jouée
    for j in range(5):
        part_1.append([[60, 80]])
    # note arrêtée
    for k in range(5):
        part_1.append([])
part["partitions"].append(part_1)
        
part_2 = []
for i in range(5):
    # note jouée
    for j in range(1):
        part_2.append([[50, 100]])
    # note arrêtée
    for k in range(19):
        part_2.append([])
part["partitions"].append(part_2)

# Json
data = json.dumps(part)

f = "drum_test.json"
fichier = "/media/data/3D/projets/darknet-letters/letters/midi/json/"
mode = "w"
tools.write_data_in_file(data, fichier + f, mode)


FPS = 60
fonts = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
root = "/media/data/3D/projets/darknet-letters/letters"

# Joue le 1er json
directory = root + "/midi/json"
extentions = [".json"]
file_list = get_file_list(directory, extentions)
json_file = file_list[0]
play_json(json_file, FPS, fonts)
