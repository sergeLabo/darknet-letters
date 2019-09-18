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


import os, sys
import random
from pymultilame import MyTools

# Import du dossier parent soit letters
# Pas d'import possible direct du dossier parent
# ValueError: attempted relative import beyond top-level package
sys.path.append("..")
from letters_path import LettersPath

lp = LettersPath()
letters_dir = lp.letters_dir
CONF = lp.conf

mt = MyTools()

# Dossier des images et txt
SHOT_JPG = lp.shot_jpg_dir

# liste de toutes les images
files = mt.get_all_files_list(SHOT_JPG, '.jpg')
# Rebat les cartes pour prendre les fichiers au hazard dans les sous-dossiers
random.shuffle(files)
nb = len(files)
print("Nombre de fichiers", nb)

if nb == 0:
    print("\n\nErreur:")
    print("Définir les chemins de shot_jpg dans letters.ini\n\n")
    os._exit(0)

train_num = int(0.9*nb)

counter = 0
train = ""
test = ""

for f in files:
    if counter < train_num:
        train += f + "\n"
    else:
        test += f + "\n"
    counter += 1

# Ecriture dans les fichiers
mt.write_data_in_file(test, "test.txt", "w")
mt.write_data_in_file(train, "train.txt", "w")

print("Done.")
