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
        print("\nFrame rate =", fps, "\n")
        
        # #for instrum in gl.instruments:
            # #print("thread_dict de", instrum, "=", gl.pomn[instrum].thread_dict)
        
        gl.time = time()


def get_frame_notes():
    """
    gl.partitions  = [[partition_1, partition_2 ......],]

    gl.partitions[0] = [[], [], [], [[64, 90]], [[64, 90]], [[64, 90]],
        [[64, 90]], [[66, 90]], [[66, 90]], [[66, 90]], [[66, 90]], [], [],
        [], [], [[68, 90]], [[68, 90]], [[68, 90]], ...]

    gl.instruments = [instrument_1.program,
                      instrument_2.program, ...]
                   = [75, 105]

    frame_data = [[[67, 64], [25, 47]], [[36, 64], [43, 40]]], ...
            instrum 1         2           3         4
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

    # instrument est le numéro de la bank, une police par instrument
    # frame_data = [[], []] note_tuple = [67, 64]
    new_notes = []

    if frame_data:
        #print(frame_data)
        # frame_data = [[[69, 90]], [[45, 64]]]
        #               instrum_0     instrum_0
        for note_partition in frame_data:
            # frame_data = [[[67, 64]], [[25, 47]]]
            # note_partition = [[67, 64]]
            if note_partition:
                font = frame_data.index(note_partition)
                instrument = gl.instruments[font]
                # la liste est dans une liste
                note = note_partition[0][0]
                volume = note_partition[0][1]

                # Affichage et play
                display((note, volume), font)
                play_note(instrument, note, volume)
                new_notes.append((instrument, note))

        # Arrêt des notes si plus dans la liste
        stop_notes(new_notes)


def play_note(instrument, note, volume):
    """thread_dict = {69: 1, 48: 1, 78:0} """

    # Vérification que la note n'est pas en cours
    en_cours = 0
    if note in gl.pomn[instrument].thread_dict:
        if gl.pomn[instrument].thread_dict[note] == 1:
            en_cours = 1
            
    # Lancement de la note si pas en cours
    if not en_cours:
        # Lancement d'une note
        gl.pomn[instrument].thread_note(note, volume)


def stop_notes(new_notes):
    """Stop des notes en cours qui ne sont plus dans new_notes
    new_notes = [(instrument, note), ...]
    thread_dict = {69: 1, 48: 1, 78: 0}
    """

    for instrument in gl.instruments:
        for k, v in gl.pomn[instrument].thread_dict.items():
            if (instrument, k) not in new_notes:
                gl.pomn[instrument].thread_dict[k] = 0

    
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
    letter_obj.visible = True


def hide_unplayed_letters():
    """all_obj["font_1_f"] = obj_blender"""

    dec = 0
    for k, v in gl.all_obj.items():
        if k not in gl.obj_name_list_to_display:
            if "font" in k:  # pas les cam, lamp ...
                hide_letter(v)


def hide_letter(lettre):
    l = "abcdefghijklmnopqrstABCDEFGHIJKLMNOPQRST"
    letters = list(l)

    # font_0_a
    x = int(lettre.name[5])
    y = letters.index(lettre.name[7])
    lettre.position = x, y, 0
    lettre.visible = False


def decal_unplayed_letters(v):
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


def set_letter_unvisible(lettre):
    """Toutes les lettres sont invisible au départ"""
    lettre.visible = False
