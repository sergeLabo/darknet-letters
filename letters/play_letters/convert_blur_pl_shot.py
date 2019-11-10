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

Ce script floute et enregistre en jpg les images à faire lire par l'IA.
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

            
class BlurAndConvert:

    def __init__(self):
        self.mt = MyTools()
        self.blur_min = CONF["play_letters"]["blur_min"]
        self.blur_max = CONF["play_letters"]["blur_max"]

        # Dossiers
        self.shot = CONF["play_letters"]["pl_shot"]
        print("Dossier play_letters:", self.shot)
        self.create_shot_jpg_dir()

        # Liste des sous-dossiers avec le dossier play_letters_shot
        self.sub_directories_list = [x[0] for x in os.walk(self.shot)]
        print("Liste des sous-répertoires:", self.sub_directories_list)
        self.create_sub_directories()

        # Copie des txt
        self.copy_all_txt()
        
        # Images png
        self.all_png_files = self.mt.get_all_files_list(self.shot, '.png')
        print("Nombre de fichiers à convertir:", len(self.all_png_files))
        if len(self.all_png_files) == 0:
            print("\n\nPas d'images à convertir")
            print("Créer les images avant !")
            os._exit(0)

        # Exécution du script flou puis save
        self.save_to_jpg()

    def copy_all_txt(self):
        """
        /bla...bla/play_letters_shot/bob_sherif/instruments.txt
        to
        /bla...bla/play_letters_shot_jpg_6/bob_sherif/instruments.txt
        """
        
        # Tous les txt
        txts = self.mt.get_all_files_list(self.shot, '.txt')

        for txt in txts:
            dst = txt.replace(self.shot, self.shot_jpg)
            # Copie du fichier txt des png dans les jpg
            copyfile(txt, dst)

    def create_shot_jpg_dir(self):
        self.shot_jpg = self.shot + "_jpg"
        
        print("Dossier pl_shot_jpg:", self.shot_jpg)
        # Si le dossier n'existe pas, je le crée
        self.mt.create_directory(self.shot_jpg)

    def create_sub_directories(self):
        """Création des sous dossiers."""

        for sd in self.sub_directories_list:
            if sd != self.shot:
                print("Sous répertoire en png:", sd)
                # Soustraction du chemin de shot_dir
                shot_dir = Path(self.shot)
                a = str(sd).replace(str(shot_dir), "")
                # Ajout du chemin de jpg_dir
                b = Path(str(self.shot_jpg) + a)
                print("Sous répertoire en jpg:", b)
                self.mt.create_directory(b)

    def apply_blur(self, img):

        blur = random.randint(self.blur_min, self.blur_max)
        if blur != 0:
            img = cv2.blur(img, (blur, blur))
        return img

    def save_to_jpg(self):
        n = 0

        for png in self.all_png_files:
            if n % 100 == 0 and n != 0:
                a = len(self.all_png_files)
                print("Nombre de fichiers convertis:", n, "sur", a)
            n += 1
            # print(png)
            
            # Lecture de png
            img = cv2.imread(png)

            # Flou
            img = self.apply_blur(img)

            # On travaille avec Path
            png_path = Path(png)
            jpg_path = self.get_jpg_name(png_path)  # PosixPath

            # Ecriture de l'image jpg, cv2 prend seulement path en str
            cv2.imwrite(str(jpg_path), img,
                                       [int(cv2.IMWRITE_JPEG_QUALITY),
                                       100])

            # On prend son temps
            sleep(0.01)

        print("Nombre de fichiers convertis:", n)
        
    def get_jpg_name(self, png_path):
        """ png = str
        png = str(self.shot)     + /25/shot_4126.png = str
        jpg = str(self.shot_jpg) + /25/shot_4126.jpg = str
        """

        # Soustraction du chemin de shot_dir
        a = str(png_path).replace(str(self.shot), "")
        # Ajout du chemin de jpg_dir
        b = Path(str(self.shot_jpg) + a)

        # Changement de l'extension
        jpg_path = b.with_suffix(".jpg")

        return jpg_path


if __name__ == "__main__":

    BlurAndConvert()
