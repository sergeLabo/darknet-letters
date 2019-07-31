#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


from time import sleep
import numpy as np
import cv2

from pymultilame import MyTools

tools = MyTools()


def cvDrawBoxes(img, coords):
    """Dessine le rectangle avec centre(cx, cy) et taille w et h"""
    
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
    return img


def verif():
    rep = "/media/data/3D/projets/darknet-letters/letters/shot/"
    pngs = tools.get_all_files_list(rep, "png")
    nom = "/media/data/3D/projets/darknet-letters/letters/control/shot_rect/"

    loop = 1
    a = 0
    while loop:
        img = cv2.imread(pngs[a])
        # Toutes les lignes
        lines = tools.read_file(pngs[a][:-4] + ".txt")
        # Les lignes en list
        lines = lines.splitlines()
        # #print(lines)
        for line in lines:
            # #print(line)
            line = line.split(" ")
            img = cvDrawBoxes(img, line)
                
        if lines:
            n = pngs[a].split(rep)
            m = n[1][2:-4]
            name = nom + m + "_rect.png"
            # #print(m)
            cv2.imwrite(name, img)
            sleep(0.01)
            
        a += 1
        if a == len(pngs):
            loop = 0
        # Echap, attente
        k = cv2.waitKey(33)
        if k == 27:
            loop = 0

    cv2.destroyAllWindows()


def display():
    nom = "/media/data/3D/projets/darknet-letters/letters/control/shot_rect/"
    pngs = tools.get_all_files_list(nom, "png")
    loop = 1
    a = 0
    while loop:
        img = cv2.imread(pngs[a])
        cv2.imshow("Control", img)
        a += 1
        if a == len(pngs):
            loop = 0    
         # Echap, attente
        k = cv2.waitKey(100)
        if k == 27:
            loop = 0   


if __name__ == '__main__':
    verif()
    display()
