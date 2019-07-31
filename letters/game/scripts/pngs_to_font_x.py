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
    Crée les images qui rassemble les images individuelles des lettres
    dans le dossier textures.
    
Copier le dossier pngs
de
        /media/data/3D/projets/darknet-letters/letters/ttf_to_png
dans
        /media/data/3D/projets/darknet-letters/letters/game/textures
"""


import os, sys
import numpy as np
from itertools import product
import cv2

from pymultilame import MyTools


def directory_rename():

    mt = MyTools()
    rep_num = 0
    rep = "/media/data/3D/projets/darknet-letters/letters/game/textures/pngs"

    sub_dirs = mt.get_all_sub_directories(rep)
    # sub_dirs comprend pngs qui est le root
    del sub_dirs[0]

    for sb in sub_dirs:
        dst = rep + "/font_" + str(rep_num)
        print(sb, dst)
        os.rename(sb, dst)
        rep_num += 1


def get_square_image():
    """Agrandi les images en largeur pour les avoir carrées"""

    mt = MyTools()

    # La liste de tous les font_a
    rep = "/media/data/3D/projets/darknet-letters/letters/game/textures/pngs"
    sub_dirs = mt.get_all_sub_directories(rep)
    # sub_dirs comprend pngs qui est le root
    del sub_dirs[0]
    print(sub_dirs)

    for sb in sub_dirs:
        # Liste des images du répertoire
        imgs = mt.get_all_files_list(sb, ".png")
        for img_file in imgs:
            print("img_file", img_file)
            img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
            h, w = img.shape[0], img.shape[1]
            print(h, w)  # 337 171
            top, bottom= 0, 0
            b = int((h - w)/2)
            left = right = b
            try:
                img = cv2.copyMakeBorder(img,
                                         top, bottom, left, right,
                                         cv2.BORDER_CONSTANT,
                                         value=[0, 0, 0, 0])
            except:
                print("Largeur plus grande que hauteur pour l'image", img_file)
            cv2.imwrite(img_file, img)


def resize_at_biggest():
    """Agrandi les images à la taille de la plus grande"""

    mt = MyTools()

    # La liste de tous les font_a
    rep = "/media/data/3D/projets/darknet-letters/letters/game/textures/pngs"
    sub_dirs = mt.get_all_sub_directories(rep)
    # sub_dirs comprend pngs qui est le root
    del sub_dirs[0]

    maxi = 0
    # Recherche de l'image la plus grande
    for sb in sub_dirs:
        # Liste des images du répertoire
        imgs = mt.get_all_files_list(sb, ".png")
        for img_file in imgs:
            #print("img_file", img_file)
            img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
            h, w = img.shape[0], img.shape[1]
            if h > maxi:
                maxi = h
    print("maxi", maxi)

    # Retaillage à maxi
    for sb in sub_dirs:
        # Liste des images du répertoire
        imgs = mt.get_all_files_list(sb, ".png")
        for img_file in imgs:
            print("img_file", img_file)
            img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
            img = cv2.resize(img, (maxi, maxi), interpolation=cv2.INTER_AREA)
            cv2.imwrite(img_file, img)


def regroupage_font_images():
    """Regroupage des images de lettres d'une font, minuscule ou majuscule
    20 images 445x445
    5 x 445 = 2225 = w
    5 x 445 = 2225 = h
    abcde
    fghij
    klmno
    pqrst
    54ème ligne vide
    """

    mt = MyTools()

    textures = "/media/data/3D/projets/darknet-letters/letters/game/textures/"

    # La liste de tous les font_a
    rep = "/media/data/3D/projets/darknet-letters/letters/game/textures/pngs"
    sub_dirs = mt.get_all_sub_directories(rep)
    # sub_dirs comprend pngs qui est le root
    del sub_dirs[0]

    for sb in sub_dirs:
        # de /medi...../textures/pngs/font_6, récup de 6=font
        #font = sb[-6:][-1]
        font = sb[-1]

        # dtype=np.uint8
        minuscules = np.zeros((2225, 2225, 4))
        majuscules = np.zeros((2225, 2225, 4))

        # Liste des images du répertoire
        imgs = mt.get_all_files_list(sb, ".png")
        for img_file in imgs:
            #print("img_file", img_file)
            # position et maj_min
            position, maj_min = get_position_and_maj_min(img_file)

            if position != (-1, -1):
                # l'image
                img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)

                # agglomération des images
                if maj_min == "min":
                    minuscules = paste_image(   minuscules, img,
                                                position[0], position[1])
                else:
                    majuscules = paste_image(   majuscules, img,
                                                position[0], position[1])

        # Enreg des 2 fichiers dans le dossiers textures
        minuscule_file = textures + "minuscule_" + str(font) + ".png"
        cv2.imwrite(minuscule_file, minuscules)
        print("Enregistrement de:", minuscule_file)

        majuscules_file = textures + "majuscules_" + str(font) + ".png"
        cv2.imwrite(majuscules_file, majuscules)


def paste_image(bg, over, x, y):
    """bg = minuscules ou majuscules
    img = image d'une lettre à coller taille 445x445
    position:   0 à 5 sur largeur
                0 à 4 sur hauteur
    """

    x = x * 445
    y = y * 445

    bg = over_transparent(bg, over, x, y)

    return bg


def over_transparent(bg, over, x, y):
    """Overlay over sur bg, à la position x, y
    x, y = coin supérieur gauche de over
    """

    bg_width = bg.shape[1]
    bg_height = bg.shape[0]

    if x >= bg_width or y >= bg_height:
        return bg

    h, w = over.shape[0], over.shape[1]

    if x + w > bg_width:
        w = bg_width - x
        over = over[:, :w]

    if y + h > bg_height:
        h = bg_height - y
        over = over[:h]

        over = np.concatenate([ over,
                                np.ones((over.shape[0], over.shape[1], 1), dtype=over.dtype)* 255],
                                axis=2)

    over_image = over[..., :4]
    mask = over[..., 3:] / 255.0
    bg[y:y + h, x:x + w] = (1.0 - mask) * bg[y:y + h, x:x + w] + mask*over_image

    return bg


def get_position_and_maj_min(img_file):
    """
    /media/.../textures/pngs/font_1/A.png
    Je coupe 4 à la fin, je prends le dernier
    """

    positions = [list("abcde"),
                list("fghij"),
                list("klmno"),
                list("pqrst")]

    POSITIONS = [list("ABCDE"),
                list("FGHIJ"),
                list("KLMNO"),
                list("PQRST")]

    # La lettre est a ou A
    value = img_file[:-4][-1]

    position = find_item(positions, value)
    maj_min = "min"
    if position == (-1, -1):
        # c'est une majuscule
        position = find_item(POSITIONS, value)
        maj_min = "maj"

    print("value", value, "maj_min", maj_min, "position", position)

    return position, maj_min


def find_item(liste, item):
    """Index d'un item dans une liste de liste
    abcde
    fghij
    klmno
    pqrst
    """

    a, b = -1, -1
    for l in liste:  # abcde
        # abcde
        if item in l:
            a = l.index(item)
            b = liste.index(l)

    return a, b


def get_position(plan):
    """Le centre de l'objet est 0,0,0
    je calcule la position d e la moyenne des 4 vertices du plan
    """
    # Liste de 4 liste de 3
    vl = get_plane_vertices_position(plan)

    # Moyenne des x
    x = (vl[0][0] + vl[2][0])/2
    # Moyenne des y
    y = (vl[0][1] + vl[1][1])/2
        
    return x, y


def get_plane_vertices_position(obj):
    """Retourne les coordonnées des vertices d'un plan
    [[5.5, -4.125, 1.5], [5.5, -3.375, 1.5], [4.5, -3.375, 1.5],
                                                    [4.5, -4.125, 1.5]]
    """
    verts = []
    a = 0
    for mesh in obj.meshes:
        a += 1
        for m_index in range(len(mesh.materials)):
            for v_index in range(mesh.getVertexArrayLength(m_index)):
                verts.append(mesh.getVertex(m_index, v_index))

    vertices_list = []
    for i in range(4):
        vertices_list.append([verts[i].x, verts[i].y, verts[i].z])

    return vertices_list


if __name__ == '__main__':
    """
    Crée les images qui rassemble les images individuelles des lettres
    dans le dossier textures.
    
    Copier le dossier pngs
    de
            /media/data/3D/projets/darknet-letters/letters/ttf_to_png
    dans
            /media/data/3D/projets/darknet-letters/letters/game/textures
    """

    directory_rename()
    get_square_image()
    resize_at_biggest()
    regroupage_font_images()
