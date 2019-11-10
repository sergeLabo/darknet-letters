#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
20 lettres par police, minuscules et majuscules
10 polices
400 objets différents

Exemple:
font_2_a font_2_A font_0_z font_9_t
lettres de a à t et A à T

Version sans majuscules
"""

from pymultilame import MyTools


m = "bcdefghijklmnopqrst"
M = "BCDEFGHIJKLMNOPQRST"
MINUS = list(m)
MAJUS = list(M)


def get_objects():
    objets = []

    for font in range(10):
        for minus in MINUS:
            ob = "font_" + str(font) + "_" + minus
            objets.append(ob)
        # #for majus in MAJUS:
            # #ob = "font_" + str(font) + "_" + majus
            # #objets.append(ob)

    print(len(objets))
    print(objets)
    return objets


def save_objects_in_obj_name():

    mt = MyTools()

    f = "./obj.names"

    objects = get_objects()

    lines = ""
    for obj in objects:
        lines += obj + "\n"

    mt.write_data_in_file(lines, f, "w")

    
if __name__ == '__main__':
    save_objects_in_obj_name()
