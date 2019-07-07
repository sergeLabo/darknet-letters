#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

########################################################################
# This file is part of Darknet Midi.
#
# Darknet Midi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Darknet Midi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
########################################################################


import os, sys
from itertools import product
import cv2

from pymultilame import MyTools


def create_obj_names():
    mt = MyTools()
    
    data = ""
    for i in range(128):
        data += "n" + str(i) + "\n"
    for i in range(100):
        data += "v" + str(i) + "\n"    
    
    fichier = "./darknet/obj.names"
    mode = "w"
    mt.write_data_in_file(data, fichier, mode)


def create_obj_names_repr():
    mt = MyTools()
    
    data = ""
    for i in range(10):
        data += "nu" + str(i) + "\n"
    for i in range(10):
        data += "nd" + str(i) + "\n"
    for i in range(2):
        data += "nc" + str(i) + "\n"        
        
    for i in range(10):
        data += "vu" + str(i) + "\n"
    for i in range(10):
        data += "vd" + str(i) + "\n"   
    
    fichier = "./darknet/obj_repr.names"
    mode = "w"
    mt.write_data_in_file(data, fichier, mode)


def get_conversion_dict():
    """ 0: "nu0", """
    
    mt = MyTools()
    
    data = """#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

conversion = { """

    a = 0
    
    for i in range(10):
        data += "              " + str(a) + ': "nu' + str(i) + '",\n'
        a += 1
    for i in range(10):
        data += "              " + str(a) + ': "nd' + str(i) + '",\n'
        a += 1
    for i in range(2):
        data += "              " + str(a) + ': "nc' + str(i) + '",\n'
        a += 1
        
    for i in range(10):
        data += "              " + str(a) + ': "vu' + str(i) + '",\n'
        a += 1
    for i in range(10):
        data += "              " + str(a) + ': "vd' + str(i) + '",\n'
        a += 1

    data += "}"
    fichier = "./conversion.py"
    mode = "w"
    mt.write_data_in_file(data, fichier, mode)


def get_boolean(repeat):
    mt = MyTools()
    a = 0
    data = "boolean = {"
    for p in product(("0", "1"), repeat=repeat):
        data += str(a) + ": " + str(p) + ",\n"
        a += 1
    data += "}"
    fichier = "./boolean.py"
    mode = "w"
    mt.write_data_in_file(data, fichier, mode)


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
            img = cv2.copyMakeBorder(img,
                                     top, bottom, left, right,
                                     cv2.BORDER_CONSTANT,
                                     value=[0, 0, 0, 0])
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


            
if __name__ == '__main__':
    directory_rename()
    get_square_image()
    resize_at_biggest()
