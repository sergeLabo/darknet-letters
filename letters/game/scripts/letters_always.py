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

from pymultilame import MyTools
from pymultilame import get_all_objects, get_scene_with_name

from bge import logic as gl


def main():
    gl.tempo.update()
    #print(gl.tempo["frame"].tempo)
    
    # Pratique ça
    gl.all_obj = get_all_objects()
    
    # Reset de la liste des noms d'objet blender à afficher
    gl.obj_name_list_to_display = []
    
    # les notes de la frame
    get_frame_data()
    get_notes_in_frame_data()

    # Décalage des lettres non jouées
    hide_unplayed_letters()
    

def get_notes_in_frame_data():
    """
        gl.frame_data = [[[67, 64]], [], [[36, 64], [43, 40]], []]
                     instrum 1   2    3   4                     5

        gl.notes = {0: [], 1: ....}
    """
    gl.notes = {}
    for instrum in gl.frame_data:
        # Une police par instrument
        font = gl.frame_data.index(instrum)
        
        # instrum = [[67, 64]] ou [] ou [[36, 64], [43, 40]]
        if instrum:  # Pas d'analyse si liste vide
            for note_tuple in instrum:  # [67, 64]
                display(note_tuple, font)
                

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
                #print(letter, type(letter))
                letter_obj = gl.all_obj[ob]
                set_letter_position(letter_obj)
                

def set_letter_position(letter_obj):
    """Plage possible en position -9.6 à 9.6"""

    # Correction du décalage du centre de l'objet
    x, y, z = get_mesh_position(letter_obj)

    plagex = 1
    # #u = uniform(-plagex, plagex)
    u = numpy.random.uniform(-plagex, plagex)
    
    plagey = 1
    # #v = uniform(-plagey, plagey)
    v = numpy.random.uniform(-plagey, plagey)
    
    # les plans qui ont créés les lettres sont décalés de dh vers le haut
    # le rang du bas a été coupé
    dh = 1
    letter_obj.worldPosition = u - x, 0, v - z + dh
    
    size = uniform(0.3, 1.2)
    letter_obj.worldScale = size, size, size

    
def hide_unplayed_letters():
    """all_obj["font_1_f"] = obj_blender"""

    for k, v in gl.all_obj.items():
        if k not in gl.obj_name_list_to_display:
            if "font" in k:  # pas les cam, lamp ...
                # décalage aléatoire
                dec = uniform(5, 50)
                v.worldPosition = 20 + dec, 0, 0
                v.worldScale = 1, 1, 1


def get_frame_data():
    """
    gl.data = {0: [[52, 63], [46, 47], ...], 0: .....}
    gl.instruments = {0: "Lead Strings", 1: ...}
    pour
    gl.frame_data = [[[67, 64]], [], [[36, 64], [43, 40]], []]
                     instrum 1   2    3          4         5
    """

    # les notes de la parttition 0 seulement
    f = gl.tempo["frame"].tempo
    gl.frame_data = []
    for i in range(gl.partition_nbr):
        # [[], [], ....] [les notes de chaque instrument]
        if f < len(gl.data[0]):  # TODO trop léger
            gl.frame_data.append(gl.data[i][f])
        else:
            gl.frame_data = []
            os._exit(0)


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


def get_mesh_position(plan):
    """Le centre de l'objet est 0,0,0
    je calcule la position d e la moyenne des 4 vertices du plan
    """
    # Liste de 4 liste de 3
    vl = get_plane_vertices_position(plan)

    # Moyenne des x
    x = (vl[0][0] + vl[2][0])/2
    # Moyenne des y
    y = (vl[0][1] + vl[1][1])/2
    # Moyenne des z
    z = (vl[0][2] + vl[1][2])/2
            
    return x, y, z


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
