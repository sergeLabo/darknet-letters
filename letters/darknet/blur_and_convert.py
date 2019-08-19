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


"""
Le Blender Game engine ne permet d'enregistrer les shot qu'en png.
Darknet n'accepte que des jpg.
Bizarrement, darknet est plus efficace avec des images un peu floutées.
Ce script floute et enregistre en jpg.
"""


import os, sys
from shutil import copyfile
import cv2
import random
from time import sleep
from pathlib import Path

from pymultilame import MyTools

# Import du dossier parent soit letters
# Pas d'import possible direct du dossier parent
# ValueError: attempted relative import beyond top-level package
sys.path.append("..")
from letters_path import LettersPath

lp = LettersPath()
letters_dir = lp.letters_dir
CONF = lp.conf
shot_dir = lp.shot_dir
shot_jpg = lp.shot_jpg_dir


class BlurAndConvert:

    def __init__(self):
        self.mt = MyTools()

        # Chemin de shot
        self.shot = shot_dir
        
        self.create_shot_jpg()
        self.create_sub_directories()
        self.all_png_files = self.mt.get_all_files_list(self.shot, '.png')
        print("Nombre d'images png:", len(self.all_png_files))

        # Exécution du script flou puis save
        self.save_to_jpg()
                
    def create_shot_jpg(self):
        self.shot_jpg = shot_jpg
        # Si le dossier n'existe pas, je le crée
        self.mt.create_directory(self.shot_jpg)
        
    def create_sub_directories(self):
        """Création de 100 dossiers."""

        # Répartition dans 100 sous dossiers
        for l in range(100):
            directory = os.path.join(self.shot_jpg, str(l))
            self.mt.create_directory(directory)

    def blur(self, img):
        # Flou
        blur = CONF["darknet"]["blur"]
        k = random.randint(0, blur)
        if k != 0:
            img = cv2.blur(img, (k, k))
        return img

    def save_to_jpg(self):
        n = 0
        for png in self.all_png_files:
            if n % 100 == 0:
                print("png:", png)
            n += 1
            
            # lecture
            img = cv2.imread(png)
            img = self.blur(img)

            # Les images de 704x704 occupent toute la mémoire de la GTX1060
            # de 6 Go !
            size = CONF["darknet"]["shot_size"]
            img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
            
            # De ....  /shot/25/shot_4126.png
            # vers ..  /shot_jpg/25/shot_4126.jpg
            part = png.split("/shot/")
            # print(part)  # ['...', '0/shot_25.png']
            
            nom = part[1][:-4] + '.jpg'
            # print(nom)   # 46/shot_46'
            
            name = self.shot_jpg / nom
            # ..... /letters/shot_jpg/..jpg
            #print("jpg:", name)
            
            # Copier coller du fichiers txt
            fin = part[1][:-4] + '.txt'
            txt = self.shot / fin
            #print("txt de png:", txt)
            
            dst = self.shot_jpg / fin
            #print("txt de jpg:", dst)
            
            copyfile(txt, dst)
            
            # Ecriture
            cv2.imwrite(str(name), img, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
            sleep(0.01)


if __name__ == "__main__":
    
    BlurAndConvert()
