#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import os
from shutil import copyfile
import cv2
import random
from time import sleep
from pymultilame import MyTools


"""
Le Blender Game engine ne permet d'enregistrer les shot qu'en png.
Darknet n'accepte que des jpg.
Bizarrement, darknet est plus efficace avec des images un peu floutées.
Ce script floute et enregistre en jpg.
Il faut définir le chemin de shot ligne 24.
"""


# Définir le chemin de /shot
# TODO Reste ainsi !
SHOT = '/media/data/3D/projets/darknet-letters/letters/shot'

    
class BlurAndConvert:

    def __init__(self, shot):
        self.mt = MyTools()
        self.shot = shot
        self.create_shot_jpg()
        self.create_sub_directories()
        self.all_png_files = self.mt.get_all_files_list(self.shot, '.png')
        print("Nombre d'images png:", len(self.all_png_files))
        self.save_to_jpg()
        
    def create_shot_jpg(self):
        self.shot_jpg = self.shot.replace("/shot", "") + '/shot_jpg'
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
        k = random.randint(0, 5)
        if k != 0:
            img = cv2.blur(img, (k, k))
        return img

    def save_to_jpg(self):
        for png in self.all_png_files:
            # lecture
            img = cv2.imread(png)
            img = self.blur(img)

            # nouveau nom
            # De ....  /shot/25/shot_4126.jpg
            n = png.split("/shot/")  # 46/shot_46.png'
            nom = "/" + n[1][:-4]
            name = self.shot_jpg + nom + '.jpg'
            # ..... /letters/shot_jpg/46/shot_46.jpg
            print(name)
            
            # Copier coller du fichiers txt
            txt = png[:-4] + '.txt' 
            dst = self.shot_jpg + nom + '.txt'
            print(dst)
            copyfile(txt, dst)
            
            # Ecriture
            cv2.imwrite(name, img, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
            sleep(0.01)


if __name__ == "__main__":
    
    BlurAndConvert(SHOT)
