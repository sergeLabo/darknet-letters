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
from random import uniform, randint
import numpy
from time import time, sleep
import json

from pymultilame import MyTools
from pymultilame import get_all_objects, get_scene_with_name

from bge import logic as gl
from bge import events
from bge import render

from scripts.letters_once import main as letters_once_main
from scripts.letters_once import get_shot_init
from scripts.letters_once import music_and_letters_init
from scripts.letters_once import intro_init


HELP = """
SPACE pour relancer et changer de music\n
1 Affichage du logo\n
2 Lancement de music and letters\n
3 Lancement de get shot\n
H help\n
Echap Quitter
"""

        
def main():
    # Saisie clavier
    keyboard()

    # Affichage si besoin
    display_info()
    
    # Tous les update par frame
    gl.tempo.update()
    #print_frame_rate()

    # Phase: intro, music and letters, get shot
    if gl.phase == "intro":
        main_intro()
    if gl.phase == "music and letters":
        main_music_and_letters()
    if gl.phase == "get shot":
        main_get_shot()


def main_intro():
    if gl.info == "":
        gl.all_obj["Cube"].visible = True
        gl.info = "H = Help"  


def main_music_and_letters():
    # Aggrandissement de la fenêtre
    render.setWindowSize(1300, 1300)
    
    gl.all_obj["Cube"].visible = False

    # Reset de la liste des noms d'objet blender à afficher
    gl.obj_name_list_to_display = []

    # Joue et affiche les notes de la frame
    frame_notes = get_frame_notes()
    notes = get_notes(frame_notes)
    display_frame_notes(notes)
    play_frame_notes(notes)

    # Décalage des lettres non jouées
    hide_unplayed_letters()


def main_get_shot():
    """Shot tous les 20 frames
     5 = reset, nouvelle image de notes
    affichage fixe
    10 = enregistrement des positions
    15 = shot
    affichage fixe
    """

    gl.all_obj["Cube"].visible = False

    if gl.tempo['shot'].tempo == 5:
        # Reset de la liste des noms d'objets blender à afficher
        gl.obj_name_list_to_display = []

        # Affiche les notes de la frame
        frame_notes = get_frame_notes()
        notes = get_notes(frame_notes)
        display_frame_notes(notes)

        # Décalage des lettres non jouées
        hide_unplayed_letters()

    # Save position des lettres frame avant d'enreg
    if gl.tempo['shot'].tempo == 10:
        gl.previous_datas = get_objets_position_size()

    # Enregistre les shots
    if gl.tempo['shot'].tempo == 15:
        if gl.previous_datas:
            sub_dir = get_sub_dir()
            save_txt_file(gl.previous_datas, sub_dir)
            sleep(0.01)
            save_shot(sub_dir)
            sleep(0.01)
            gl.numero += 1

    # Fin du jeu
    end()


def get_frame_notes():
    """
    gl.partitions  = [[partition_1, partition_2 ......],]

    gl.partitions[0] = [[], [], [], [[64, 90]], [[64, 90]], [[64, 90]],
        [[64, 90]], [[66, 90]], [[66, 90]], [[66, 90]], [[66, 90]], [], [],
        [], [], [[68, 90]], [[68, 90]], [[68, 90]], ...]

    gl.instruments = [[[0, 25], false, "Bass"], [[0, 116], true, "Drums2"]]

    frame_notes = [[[67, 64], [25, 47]], [[36, 64], [43, 40]]], ...
            instrum 1         2           3         4
    il n'y a qu'une note par instrument et par frame
    45: [67, 64],      8: [], 14: []}
    """

    # Le numéro de frame de 0 à infini
    frame_notes = []

    # Si le morceau n'est pas fini
    if gl.frame < len(gl.partitions[0]):
        # Je passe les frames sans notes
        while not frame_notes:
            # si gl.partitions à 6 listes soit 6 partitions
            for partition in gl.partitions:
                frame_notes.append(partition[gl.frame])
            gl.frame += 1
    else:
        if gl.phase != "get shot":
            # Relance de get_shot.json à une frame au hazard
            gl.frame = randint(500, 2000)
            frame_notes = []
        if gl.phase != "music and letters":    
            # Kill de tous les threads et restart
            new_music()

    return frame_notes


def get_notes(frame_notes):
    """instr_num est l'index de l'instrument dans gl.instruments
    gl.instruments = [[[0, 70], False, 'Bason'], [[0, 73], False, 'Flute']]
    une police par instrument
    frame_notes = [[[1, 4]], [[1, 4]], [[1, 4]], [[1, 4]], [[1, 4]], [[1, 4]],
    [[1, 4]], [[1, 4]], [[1, 4]], [[1, 4]]]
    """

    notes = []

    if frame_notes:
        for i in range(len(frame_notes)):
            # TODO bug ici
            font = i
            # la liste est dans une liste qui pourrait avoir plusieurs notes
            # soit un accord, je ne garde que la première note
            # frame_notes[i] = [[1, 4]]
            try:
                note = frame_notes[i][0][0]
                volume = frame_notes[i][0][1]
                notes.append((font, note, volume))
            except:
                pass

    return notes


def get_sub_dir():
    """60000/100=600 fichiers par dossier
    12345/600=20
    """
    n = gl.total/100
    sub_dir = int(gl.numero/n)
    if sub_dir < 0:
        print("Sous dossier négatif")
    if sub_dir > 99:
        print("Sous dossier > 99")
    return sub_dir


def get_objets_position_size():
    """De tous les objets
    Blender:
        Dimension des lettres sans scale: 2,0,2
        Centre: 0,0,0
        Vue caméra: x = -5 à 5, y = 5 à -5
    Dans l'image:
        Origine en haut à gauche
    """

    # absolu = 10 relatif = 1
    relatif = 0.1

    # Liste des lettres affichées
    datas = ""
    for ob in gl.obj_name_list_to_display:
        # ob = nom de l'objet
        p = gl.all_obj[ob].worldPosition
        s = gl.all_obj[ob].worldScale

        # origine en 5, -5, le y est le z du centre
        x = round((p[0] + 5) * relatif, 2)
        # 3 +5 8 1-8
        y = round(1 - ((p[2] + 5) * relatif), 2)
        # Dimension
        dim = round(s[0] * 2 * relatif, 2)

        data =  ob + " " \
                + str(x) + " " \
                + str(y) + " " \
                + str(dim) + " " \
                + str(dim) + " " \
                + "\n"
        datas += data

    # Suppr du dernier fin de ligne
    datas = datas[:-2]
    return datas


def save_txt_file(datas, sub_dir):
    """<object-class> <x> <y> <width> <height>
    Sous dossier > 99
    Python script error - object 'Cube', controller 'Python1':
    Traceback (most recent call last):
      File "/media/data/3D/projets/darknet-letters/letters/game/letters.blend/labomedia_always.py", line 41, in main
      File "/media/data/3D/projets/darknet-letters/letters/game/scripts/letters_always.py", line 55, in main
        main_get_shot()
      File "/media/data/3D/projets/darknet-letters/letters/game/scripts/letters_always.py", line 109, in main_get_shot
        save_txt_file(gl.previous_datas, sub_dir)
      File "/media/data/3D/projets/darknet-letters/letters/game/scripts/letters_always.py", line 247, in save_txt_file
        gl.tools.write_data_in_file(datas, fichier, "w")
      File "/usr/local/lib/python3.7/dist-packages/pymultilame/mytools.py", line 89, in write_data_in_file
        with open(fichier, mode) as fd:
    FileNotFoundError: [Errno 2] No such file or directory: '/media/serge/data/shot/100/shot_60000.txt'
    """

    fichier = os.path.join(gl.shot_directory,
                            str(sub_dir),
                            'shot_' + str(gl.numero) + '.txt')
    gl.tools.write_data_in_file(datas, fichier, "w")


def save_shot(sub_dir):
    name_file_shot = get_name_file_shot(sub_dir)
    render.makeScreenshot(name_file_shot)
    print(gl.frame, "Shot n°", gl.numero, "dans", name_file_shot)


def get_name_file_shot(sub_dir):
    """./shot/5/shot_41254.png"""

    return os.path.join(gl.shot_directory,
                            str(sub_dir),
                            'shot_' + str(gl.numero) + '.png')


def play_frame_notes(notes):
    last_notes = []
    for note_tuple in notes:
        font, note, volume = note_tuple[0], note_tuple[1], note_tuple[2]
        # Play
        play_note(note_tuple)
        last_notes.append((font, note))

    # Arrêt des notes si plus dans la liste
    stop_notes(last_notes)


def display_frame_notes(notes):
    """Affichage"""

    for note_tuple in notes:
        font, note, volume = note_tuple[0], note_tuple[1], note_tuple[2]
        if font < 10:
            display(font, note, volume)


def display(font, note, volume):
    """Affiche ou cache les lettres"""

    # Lettres correspondantes
    cn, dn, un = conversion(note, "min")
    cv, dv, uv = conversion(volume, "maj")

    # Liste des lettres à afficher
    to_display = [un, dn, cn, uv, dv, cv]

    # Affichage des lettres
    for letter in to_display:
        if letter:
            ob = "font_" + str(font) + "_" + letter
            gl.obj_name_list_to_display.append(ob)
            letter_obj = gl.all_obj[ob]
            set_letter_position(letter_obj)
            letters_count(ob)


def letters_count(ob):
    """Comptage des lettres affichées:"""

    try:
        gl.count
    except:
        print("Création de gl.count")
        gl.count = {}

    if ob in gl.count:
        gl.count[ob] += 1
    else:
        gl.count[ob] = 1

    if gl.tempo["count"].tempo == 0:
        try:
            print("Vérification de la bonne répartition des polices:")
            print("    ", len(gl.count))
        except:
            pass


def save_count():
    """Save à la fin du jeu"""

    json_name = "./scripts/count.json"
    with open(json_name, 'w') as f_out:
        json.dump(gl.count, f_out)


def new_music():
    """Relance du jeu avec une nouvelle musique."""
    kill()

    # Enregistrement du numéro de shot déjà fait
    if gl.phase == "get shot":
        gl.ma_conf.save_config("blend", "numero", gl.numero)

    # Relance du tout
    print("Relance du jeu")
    letters_once_main()


def kill():
    """Kill de tous les threads."""

    # Fin des threads restants
    n = len(gl.instruments)
    # Seulement 10 instruments
    if n > 10: n = 10

    # Parcours de tous les threads
    for j in range(n):
        for i in range(128):
            try:
                th = gl.instruments_player[j].thread_dict[i]
                if th == 1:
                    print("thread en cours tué, instrument:", j, "thread:", j)
                gl.instruments_player[j].thread_dict[i] = 0
            except:
                pass
    sleep(1)
    print("Fin de tous les threads")

    if gl.phase == "music and letters":
        # Stop des fluidsynth.Synth() initiés
        if len(gl.instruments_player) > 0:
            for i in range(n):
                gl.instruments_player[i].stop_audio()


def keyboard():
    """
    SPACE pour relancer et changer de music
    0 pour stop du son
    1 pour start du son
    2 start de music and letters
    3 start de get shot
    7 start logo
    H help
    """

    # Changement de music
    if gl.keyboard.events[events.SPACEKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        print("\n"*2, "Restart Game")
        new_music()

    # intro
    if gl.keyboard.events[events.PAD1] == gl.KX_INPUT_JUST_ACTIVATED:
        print("Début de logo")
        gl.phase = ""
        gl.info = "Début de logo"
        gl.info_news = 1
        kill()
        intro_init()
        
    # music and letters
    if gl.keyboard.events[events.PAD2] == gl.KX_INPUT_JUST_ACTIVATED:
        print("Début de music and letters")
        gl.phase = "music and letters"
        gl.info = "Début de music and letters"
        gl.info_news = 1
        music_and_letters_init()    

    # get shot
    if gl.keyboard.events[events.PAD3] == gl.KX_INPUT_JUST_ACTIVATED:
        print("Début de get shot")
        gl.phase = "get shot"
        gl.info = "Début de get shot"
        gl.info_news = 1    
        get_shot_init()
        
    # Help
    if gl.keyboard.events[events.HKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        print("Début de help")
        gl.all_obj["Cube"].visible = False     
        gl.info = HELP
        gl.info_news = 1    

        
def display_info():
    """Lancé à chaque frame, tout le temps"""

    gl.all_obj["Text_info"]["Text"] = gl.info

    if gl.info_news:
        gl.tempo["info"].reset()
        gl.info_news = 0
        
    if gl.tempo["info"].tempo > 175:
        gl.info = ""
        

def print_frame_rate():
    sec = gl.tempo["seconde"].tempo
    if sec == 0:
        fps = int(60 / (time() - gl.time))
        print("\nFrame rate =", fps,
              "de", gl.midi_json, "\n")
        gl.time = time()


def play_note(note_tuple):
    """thread_dict = {69: 1, 48: 1, 78:0}
    instrument = (0, 25)
    """

    instr_num, note, volume = note_tuple

    # Lancement de la note si pas en cours
    if not gl.instruments_player[instr_num].thread_dict[note]:
        # Lancement d'une note
        gl.instruments_player[instr_num].thread_play_note(note, volume)


def stop_notes(last_notes):
    """Stop des notes en cours qui ne sont plus dans last_notes
    last_notes = [(instrument, note), ...]
    thread_dict = {(69, 72): 1, (1, 78): 0}
    """

    for i in range(len(gl.instruments_player)):
        for k, v in gl.instruments_player[i].thread_dict.items():
            # k = 56 = note
            if (i, k) not in last_notes:
                gl.instruments_player[i].thread_dict[k] = 0


def set_letter_position(letter_obj):
    """Réglage visuel"""

    plagex = 4.6
    u = numpy.random.uniform(-plagex, plagex)

    plagey = 4.6
    v = numpy.random.uniform(-plagey, plagey)

    un_peu_haut = 0
    letter_obj.worldPosition = u , 0, v - un_peu_haut

    size = numpy.random.uniform(0.4, 1.1)
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
    """lettre = font_1_q, récup du 1 et du q"""

    l = "abcdefghijklmnopqrstABCDEFGHIJKLMNOPQRST"
    letters = list(l)

    x = int(lettre.name[5])
    # index ok
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
    """note = 35 = l e, 30 = l et pas d'unité avec casse = min
    valable aussi pour volume à la place de note avec casse=maj
    Les a et A ne sonjt pas utilisés, donc 380 objets différents.
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

    return c, d, u


def set_letter_unvisible(lettre):
    """Toutes les lettres sont invisible au départ"""
    lettre.visible = False


def end():
    if gl.numero == gl.nombre_shot_total:
        save_count()
        gl.endGame()
