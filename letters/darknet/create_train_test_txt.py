#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import random
from pymultilame import MyTools

mt = MyTools()

# Dossier des images et txt
SHOT_JPG = '/media/data/3D/projets/darknet-letters/letters/shot_jpg'

# liste de toutes les images
files = mt.get_all_files_list(SHOT_JPG, '.jpg')
# Rebat les cartes pour prendre les fichiers au hazard dans les sous-dossiers
random.shuffle(files)
nb = len(files)
print("Nombre de fichiers", nb)

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
