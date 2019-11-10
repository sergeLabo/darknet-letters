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
import numpy as np
import cv2
import re
import time
from random import randint
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
shot_control_dir = lp.shot_control_dir

# Définir le chemin des shot à contrôler dans letters.ini
shot_jpg_dir = lp.shot_jpg_dir
    
tools = MyTools()


def cvDrawBoxes(img, coords):
    """Dessine le rectangle avec centre(cx, cy) et taille w et h"""

    # taille des images
    size = img.shape[0]
    
    # Rectangle
    cx = float(coords[1]) * size
    cy = float(coords[2]) * size
    w = float(coords[3]) * size
    h = float(coords[4]) * size

    xmin = int(cx - w/2)
    ymin = int(cy - h/2)
    xmax = int(cx + w/2)
    ymax = int(cy + h/2)

    pt1 = (xmin, ymin)
    pt2 = (xmax, ymax)

    cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)

    # Texte
    text = coords[0]
    put_text(img, text, (xmin, ymin-4), 0.4, 2)
    
    return img


def put_text(img, text, xy, size, thickness):
    """
    Adding Text to Images:
        Text data that you want to write
        Position coordinates of where you want put it (i.e. bottom-left corner
        where data starts).
        Font type (Check cv.putText() docs for supported fonts)
        Font Scale (specifies the size of font)
        regular things like color, thickness, lineType etc. For better look,
        lineType = cv.LINE_AA is recommended.

    We will write OpenCV on our image in white color.
    font = cv.FONT_HERSHEY_SIMPLEX
    cv.putText(img, 'OpenCV', (10, 500), font, 4, (255,255,255), 2, cv.LINE_AA)
    """

    cv2.putText(img,
                text,
                (xy[0], xy[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                size,
                [0, 255, 255],
                thickness,
                cv2.LINE_AA)


def get_sorted_files(fli):

    files_list = [0]*len(fli)
    for image in fli:
        # ../truc/s_j_to_i_2677.jpg s_j_to_i_2677.jpg
        nbr = image.split("/")[-1].split("_")[-1][:-4]  # 2677
        files_list[int(nbr)] = image
        
    return files_list

        
def save_control():
    # Création du dossier control/shot_control
    tools.create_directory(shot_control_dir)

    # Contrôle possible des png et jpg
    jpgs = tools.get_all_files_list(shot_jpg_dir, [".jpg", ".png"])
    print("Nombre de fichiers à contrôler:", len(jpgs))
    if len(jpgs) == 0:
        print("\n\nPas d'images à contrôler")
        print("Il faut les convertir en jpg avant !")
        os._exit(0)

    # Tri par numéro
    #jpgs = get_sorted_files(jpgs_list)
    
    loop = 1
    jpg = 0
    while loop:
        print("Image jpg ou png:", jpgs[jpg])
        img = cv2.imread(jpgs[jpg])
        
        # Toutes les lignes
        print("Fichier txt:",jpgs[jpg][:-4] + ".txt")
        lines = tools.read_file(jpgs[jpg][:-4] + ".txt")
        
        # Les lignes en list
        lines = lines.splitlines()

        for line in lines:
            line = line.split(" ")
            img = cvDrawBoxes(img, line)

        # darknet-letters/letters/control/shot_control/shot_1.jpg
        parts = jpgs[jpg].split("/")
        img_name = parts[-1]
        
        name = shot_control_dir / img_name
        print("Save to:", str(name))

        cv2.imwrite(str(name), img)
        time.sleep(0.01)

        # Stop à 200 maxi
        if jpg == 200:
            loop = 0
        if jpg == len(jpgs)-1:
            loop = 0
        jpg += 1
        # Echap, attente
        k = cv2.waitKey(1000)
        if k == 27:
            loop = 0

    cv2.destroyAllWindows()


def display():
    print("Dossier shot_control", shot_control_dir)
    
    jpgs = tools.get_all_files_list(shot_control_dir, [".jpg", ".png"])
    print("Nombre de fichiers à contrôler:", len(jpgs))
    
    loop = 1
    jpg = 0
    while loop:
        img = cv2.imread(jpgs[jpg])
        img = cv2.resize(img, (1250, 1250), interpolation=cv2.INTER_AREA)
        cv2.imshow("Control", img)
        if jpg == len(jpgs)-2:
            loop = 0
        jpg += 1
         # Echap, attente
        k = cv2.waitKey(2000)
        if k == 27:
            loop = 0


if __name__ == '__main__':

    save_control()
    display()
