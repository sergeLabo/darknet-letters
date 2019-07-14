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
Lancé à chaque frame durant tout le jeu.
"""


import os
from random import uniform
import numpy
from time import time, sleep

from pymultilame import MyTools
from pymultilame import get_all_objects, get_scene_with_name

from bge import logic as gl


def main():
    gl.tempo.update()
    print_frame_rate()
    sleep(0.016)
    
    # Pratique ça
    gl.all_obj = get_all_objects()
    
    # Reset de la liste des noms d'objet blender à afficher
    gl.obj_name_list_to_display = []
    
    # les notes de la frame
    get_frame_notes()

    # Décalage des lettres non jouées
    hide_unplayed_letters()
    

def print_frame_rate():
    sec = gl.tempo["seconde"].tempo
    if sec == 0:
        fps = int(60 / (time() - gl.time))
        print("Frame rate =", fps)
        gl.time = time()


def get_frame_notes():
    """
    gl.partitions  = [partition_1, partition_2 ......],
    gl.instruments = [instrument_1.program,
                      instrument_2.program, ...]
    pour
    frame_data = [[[67, 64], [25, 47]], [], [[36, 64], [43, 40]]], ...
            instrum 1          2    3         4          5
    il n'y a qu'une note par instrument et par frame
    45: [67, 64],      8: [], 14: []}
           
    """

    # Le numéro de frame de 0 à infini
    fr = gl.tempo["frame"].tempo
    frame_data = []
    
    # Si le morceau n'est pas fini
    if fr < len(gl.partitions[0]):
        # si gl.partitions à 6 listes soit 6 partitions
        for partition in gl.partitions:
            frame_data.append(partition[fr])
    else:
        # je kill
        #os._exit(0)
        frame_data = []
        
    # instrument est le numéro de la bank, valeur perdue non visualisée
    # Une police par instrument
    # frame_data = [[], []] note_tuple = [67, 64]
    pretty = ""
    if frame_data:
        pretty = []
        for note_partition in frame_data:
            # frame_data = [[[67, 64]], [[25, 47]]]
            # note_partition = [[67, 64]] 
            if note_partition:
                font = frame_data.index(note_partition)
                # la liste est dans une liste
                note = note_partition[0][0]
                volume = note_partition[0][1]

                # Affichage
                display((note, volume), font)

                # Terminal
                pretty.append(((note, volume), font))
    if fr % 60 == 0:
        print("note_tuple, font:", pretty)


def display(note_tuple, font):

    note = note_tuple[0]  # 35 = m f
    volume = note_tuple[1]  # 32 = M  B

    # Lettres correspondantes
    cn, dn, un = conversion(note, "min")
    cv, dv, uv = conversion(volume, "maj")

    # Liste des lettres à afficher
    to_display = [un, dn, cn, uv, dv, cv]

    # Affichage des lettres
    for letter in to_display:
        if font < 10:
            if letter:
                ob = "font_" + str(font) + "_" + letter
                gl.obj_name_list_to_display.append(ob)
                letter_obj = gl.all_obj[ob]
                set_letter_position(letter_obj)
                

def set_letter_position(letter_obj):
    """Réglage visuel"""

    plagex = 4.0
    u = numpy.random.uniform(-plagex, plagex)
    
    plagey = 4.0
    v = numpy.random.uniform(-plagey, plagey)
    
    un_peu_haut = 0
    letter_obj.worldPosition = u , 0, v - un_peu_haut

    size = numpy.random.uniform(0.1, 1.1)
    letter_obj.worldScale = size, size, size

    
def hide_unplayed_letters():
    """all_obj["font_1_f"] = obj_blender"""

    dec = 0
    for k, v in gl.all_obj.items():
        if k not in gl.obj_name_list_to_display:
            if "font" in k:  # pas les cam, lamp ...
                # décalage sur y
                v.worldPosition = 50, dec, 0
                v.worldScale = 1, 1, 1
                dec += 0.1


def get_pos_nums(num):
    """retourne une liste de unité à centaine"""
    pos_nums = []
    while num != 0:
        pos_nums.append(num % 10)
        num = num // 10
    return pos_nums

    
def conversion(note, casse):
    """35 = l e, 30 = l et pas d'unité
    valable aussi pour volume à la place de note
    """

    # Table de conversion
    if casse == "min":
        #    0123456789
        U = "abcdefghij"
        UNITE = list(U)
        #    123456789
        D = "klmnopqrs"
        DIZAINE = list(D)
        #    1
        C = "t"
        CENTAINE = list(C)

    if casse == "maj":
        #    0123456789
        U = "ABCDEFGHIJ"
        UNITE = list(U)
        #    123456789
        D = "KLMNOPQRS"
        DIZAINE = list(D)
        #    1
        C = "T"
        CENTAINE = list(C)


    # get nombre d'unité, diz, cent
    l_num = get_pos_nums(note)
    if note == 0:
        unite = None
        dizaine = None
        centaine = None
    elif 0 < note < 10:
        unite = l_num[0]
        dizaine = None
        centaine = None
    elif 9 < note < 100:
        unite = l_num[0]
        if unite == 0:
            unite = None
        dizaine = l_num[1]
        centaine = None
    elif note > 99:
        unite = l_num[0]
        if unite == 0:
            unite = None        
        dizaine = l_num[1]
        if dizaine == 0:
            dizaine = None        
        centaine = 1
    elif note > 127:
        unite = None
        dizaine = None
        centaine = None

    # Conversion en lettres
    if unite:
        u = UNITE[unite]
    else:
        u = None
    if dizaine:
        d = DIZAINE[dizaine-1] # pas de zéro
    else:
        d = None
    if centaine:
        c = CENTAINE[centaine-1] # pas de zéro
    else:
        c = None
    #print("Note", note, "=", centaine, dizaine, unite, "soit", c, d, u)
    
    return c, d, u



    # ## Correction du décalage du centre de l'objet
    # #x, y, z = get_mesh_position(letter_obj)
    
    # ## TODO Erreur sur z dû à ???
    # #bad = "bcdefkpBCDEFKP"
    # #z_error = 0
    # #for l in bad:
        # #a = "_" + l
        # #if a in letter_obj.name: 
            # #z_error = 2
            # #break

                # Pour debug
    #letter_obj.worldPosition =  -x , -y, -z + z_error - un_peu_haut
    
# #def get_mesh_position(plan):
    # #"""Le centre de l'objet est 0,0,0
    # #je calcule la position d e la moyenne des 4 vertices du plan
    # #"""
    # ## Liste de 4 liste de 3
    # #vl = get_plane_vertices_position(plan)

    # ## Moyenne des x
    # #x = (vl[0][0] + vl[2][0])/2
    # ## Moyenne des y
    # #y = (vl[0][1] + vl[1][1])/2
    # ## Moyenne des z
    # #z = (vl[0][2] + vl[1][2])/2
            
    # #return x, y, z


# #def get_plane_vertices_position(obj):
    # #"""Retourne les coordonnées des vertices d'un plan
    # #[[5.5, -4.125, 1.5], [5.5, -3.375, 1.5], [4.5, -3.375, 1.5],
                                                    # #[4.5, -4.125, 1.5]]
    # #"""
    # #verts = []
    # #a = 0
    # #for mesh in obj.meshes:
        # #a += 1
        # #for m_index in range(len(mesh.materials)):
            # #for v_index in range(mesh.getVertexArrayLength(m_index)):
                # #verts.append(mesh.getVertex(m_index, v_index))

    # #vertices_list = []
    # #for i in range(4):
        # #vertices_list.append([verts[i].x, verts[i].y, verts[i].z])

    # #return vertices_list
