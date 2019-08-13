#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import numpy as np
import cv2
import re
import time
from random import randint
from pathlib import Path

from pymultilame import MyTools


# Définir ce chemin
SHOT = "/media/data/3D/projets/darknet-letters/letters/shot_jpg"
    
tools = MyTools()


def cvDrawBoxes(img, coords):
    """Dessine le rectangle avec centre(cx, cy) et taille w et h"""

    # Rectangle
    cx = float(coords[1]) * 704
    cy = float(coords[2]) * 704
    w = float(coords[3]) * 704
    h = float(coords[4]) * 704

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

                
def verif(root, shot):
    jpgs = tools.get_all_files_list(shot, ".jpg")
    loop = 1
    a = 0
    print("Nombre de fichiers à contrôler:", len(jpgs))
    while loop:
        img = cv2.imread(jpgs[a])
        # Toutes les lignes
        lines = tools.read_file(jpgs[a][:-4] + ".txt")
        # Les lignes en list
        lines = lines.splitlines()

        for line in lines:
            line = line.split(" ")
            img = cvDrawBoxes(img, line)

        if lines:
            # darknet-letters/letters/control/shot_rect/shot_1_rect.png
            n = jpgs[a].split("/")
            m = n[-1][:-4]
            
            # m = shot_1
            shot_rect = root + "/shot_rect/"
            name = shot_rect + m + "_rect.jpg"
            print(name)
            
            cv2.imwrite(name, img)
            time.sleep(0.01)

        # Stop à 200 maxi
        if a == 200 or a == (len(jpgs)-1):
            loop = 0
        a += 1
        # Echap, attente
        k = cv2.waitKey(1000)
        if k == 27:
            loop = 0

    cv2.destroyAllWindows()


def display(root):
    shot_rect = root + "/shot_rect/"
    jpgs = tools.get_all_files_list(shot_rect, "png")
    loop = 1
    a = 0
    while loop:
        img = cv2.imread(jpgs[a])
        cv2.imshow("Control", img)
        a += 1
        if a == len(jpgs):
            loop = 0
         # Echap, attente
        k = cv2.waitKey(300)
        if k == 27:
            loop = 0


if __name__ == '__main__':

    root = str(Path.cwd().resolve())
    print("Chemin du dossier courant de analyse_play_midi:", root)
    
    # root = .... /control
    verif(root, SHOT)
    display(root)
