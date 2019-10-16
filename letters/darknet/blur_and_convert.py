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

        # Dossiers
        self.shot = shot_dir
        print("Dossier shot:", self.shot)
        self.create_shot_jpg()
        self.create_sub_directories()

        # Images png
        self.all_png_files = self.mt.get_all_files_list(self.shot, '.png')
        print("Nombre de fichiers à convertir:", len(self.all_png_files))
        if len(self.all_png_files) == 0:
            print("\n\nPas d'images à convertir")
            print("Créer les images avant !")
            os._exit(0)

        # Exécution du script flou puis save
        self.save_to_jpg()

    def create_shot_jpg(self):
        self.shot_jpg = shot_jpg
        print("Dossier shot_jpg:", self.shot_jpg)
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
        blur_mini = CONF["darknet"]["blur_mini"]
        blur_maxi = CONF["darknet"]["blur_maxi"]
        k = random.randint(blur_mini, blur_maxi)
        if k != 0:
            img = cv2.blur(img, (k, k))
        return img

    def save_to_jpg(self):
        n = 0
        size = CONF["darknet"]["shot_size"]

        for png in self.all_png_files:
            if n % 100 == 0 and n != 0:
                a = len(self.all_png_files)
                print("Nombre de fichiers convertis:", n, "sur", a)
            n += 1

            # Lecture de png
            img = cv2.imread(png)

            # Flou
            img = self.blur(img)

            # Retaillage avec size de letters.ini
            img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)

            # On travaille avec Path
            png_path = Path(png)
            jpg_path = self.get_jpg_name(png_path)  # PosixPath
            
            # Ecriture de l'image jpg, cv2 prend seulement path en str
            cv2.imwrite(str(jpg_path), img,
                                       [int(cv2.IMWRITE_JPEG_QUALITY),
                                       100])
            
            # Copie du fichier txt de png dans jpg
            txt, dst = self.get_txt_dst(png_path, jpg_path)
            copyfile(txt, dst)

            # On prend son temps
            sleep(0.01)
            
        print("Nombre de fichiers convertis:", n)

    def get_jpg_name(self, png_path):
        """ png = str
        png = str(self.shot)     + /25/shot_4126.png = str
        jpg = str(self.shot_jpg) + /25/shot_4126.jpg = str
        """

        # Soustraction du chemin de shot_dir
        a = str(png_path).replace(str(shot_dir), "")
        # Ajout du chemin de jpg_dir
        b = Path(str(shot_jpg) + a)

        # Changement de l'extension
        jpg_path = b.with_suffix(".jpg")

        return jpg_path
            
    def get_txt_dst(self, png_path, jpg_path):
        
        txt_path = png_path.with_suffix(".txt")
        dst_path = jpg_path.with_suffix(".txt")

        return txt_path, dst_path

            
if __name__ == "__main__":

    BlurAndConvert()
