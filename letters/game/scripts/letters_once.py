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
Ce script est appelé par main_init.main dans blender
Il ne tourne qu'une seule fois pour initier les variables
qui seront toutes des attributs du bge.logic (gl)
Seuls les attributs de logic sont stockés en permanence.

Il est relancé par main de letters_always à la fin du morceau.

suspendDynamics(False)
"""


import os, sys
from time import sleep
import json
from pathlib import Path
import random

from bge import logic as gl
from bge import render
from bge import texture

from pymultilame import MyConfig, MyTools, Tempo
from pymultilame import TextureChange, get_all_objects

# Ajout du dossier courant dans lequel se trouve le dossier my_pretty_midi
CUR_DIR = Path.cwd()

# Chemin du dossier letters
LETTERS_DIR = CUR_DIR.parent
sys.path.append(str(LETTERS_DIR) + "/midi")
print(str(LETTERS_DIR))

# analyse_play_midi est dans /midi
from analyse_play_midi import OneInstrumentPlayer


# Pour retrouver le début du jeu dans le terminal
print("\n"*20)


def get_conf():
    """Récupère la configuration depuis le fichier *.ini."""
    gl.tools =  MyTools()

    gl.letters_dir = str(LETTERS_DIR.resolve())

    # Dossier *.ini
    ini_file = gl.letters_dir + "/letters.ini"
    gl.ma_conf = MyConfig(ini_file)
    gl.conf = gl.ma_conf.conf


def set_tempo():

    # Création des objects
    tempo_liste = [ ("cube", 9999999999),
                    ("seconde", 60),
                    ("shot", int(gl.conf['blend']['shot_every'])),
                    ("info", 180)]

    gl.tempo = Tempo(tempo_liste)
    gl.frame_rate = 0
    gl.time = 0


def set_all_letters_position():
    """Etalement des lettres name = k"""

    l = "abcdefghijklmnopqrstABCDEFGHIJKLMNOPQRST"
    letters = list(l)

    for k, v in gl.all_obj.items():
        if "font" in k:
            # font_0_a
            x = 25 + int(k[5])
            # index ok
            y = letters.index(k[7])
            v.position = x, y, 0


def set_variable():

    # Musique
    gl.frame = 0
    gl.notes = {}
    gl.obj_name_list_to_display = []
    gl.partitions = []
    gl.instruments = []

    # Tous les objets
    gl.all_obj = get_all_objects()
    gl.info = ""
    gl.info_news = 0
    gl.all_obj["Text_info"]["Text"] = gl.info

    gl.previous_datas = ""
    gl.numero = 0
        
    # Dimension des fenêtres
    gl.music_size = gl.conf["music_and_letters"]["music_size"]

    # Position et dimension des lettres
    gl.plage_x = gl.conf["blend"]["plage_x"]
    gl.plage_y = gl.conf["blend"]["plage_y"]

    # Eclairage
    gl.sun = gl.all_obj["Sun"]

    # Avec ou sans majuscules
    gl.majuscules = gl.conf["play_letters_shot"]["volume"]

    
def get_obj_num():
    """Dict de correspondance nom de l'objet:numéro"""

    gl.letters_num = {}

    lines = gl.tools.read_file("./scripts/obj.names")
    # Les lignes en list
    lines = lines.splitlines()
    for i in range(len(lines)):
        gl.letters_num[lines[i]] = i


def set_video():

    gl.plane = gl.all_obj["Video"]
    # identify a static texture by name
    matID = texture.materialID(gl.plane, 'MAblack')

    # create a dynamic texture that will replace the static texture
    gl.my_video = texture.Texture(gl.plane, matID)

    # define a source of image for the texture, here a movie
    try:
        film = "Astrophotography-Stars-Sunsets-Sunrises-Storms.ogg"
        movie = "./video/" + film
        print('Movie =', movie)
    except:
        print("Une video valide doit être définie !")

    try:
        s = os.path.getsize(movie)
        print("Taille du film:", s)
    except:
        print("Problème avec la durée du film !")

    gl.my_video.source = texture.VideoFFmpeg(movie)
    gl.my_video.source.scale = False

    # Infinite loop
    gl.my_video.source.repeat = -1

    # Vitesse normale: < 1 ralenti, > 1 accélère
    gl.my_video.source.framerate = 1.4

    # quick off the movie, but it wont play in the background
    gl.my_video.source.play()


def create_directories():
    """Création de 100 dossiers pour letters."""

    # Dossier d'enregistrement des images
    gl.shot_directory = gl.conf['letters_shot']["shot"]

    # Création du dossier si n'existe pas
    gl.tools.create_directory(gl.shot_directory)

    print("Dossier des shots:", gl.shot_directory)

    # Un dossier réparti dans 100 sous dossiers
    for l in range(100):
        directory = os.path.join(gl.shot_directory, str(l))
        gl.tools.create_directory(directory)


def get_file_list(directory, extentions):
    """Retourne la liste de tous les fichiers avec les extentions de
    la liste extentions
    """

    file_list = []
    for path, subdirs, files in os.walk(directory):
        for name in files:
            for extention in extentions:
                if name.endswith(extention):
                    file_list.append(str(Path(path, name)))

    return file_list


def get_get_shot_json():

    gl.midi_json = str(LETTERS_DIR) + "/get_json_to_get_shot/get_shot.json"

    with open(gl.midi_json) as f:
        data = json.load(f)
    f.close()
    
    gl.partitions = data["partitions"]  # [partition_1, partition_2 ..
    gl.instruments = data["instruments"]  # [instrument_1.program, ...
    gl.partition_nbr = len(gl.partitions)

    print("\nNombre d'instrument:", gl.partition_nbr)
    print("Nombre de notes du morceau en frame:", len(gl.partitions[0]))


def fonts_shuffle(name):
    """Le désordre des polices permet de rendre aléatoire
    le choix de la police pour chaque instrument.
    liste en désordre = [9, 5, 1, 4 ...] 10 items
    gl.fonts_list = [police assignée]
    """

    L = [*range(10)]
    random.shuffle(L)

    gl.fonts_list = []
    n = gl.partition_nbr
    
    if n >= 10:
        n = 10
        
    for i in range(n):
        gl.fonts_list.append(L[i])

    # Spécial pour benchmark, pour ces 6 fichiers
    if "oh les filles" in name:
        gl.fonts_list = [8, 7, 9, 5, 4, 1, 6]
    if "zorro" in name:
        gl.fonts_list = [9, 4, 2]
    if "On Ira Tous Au Paradis" in name:
        gl.fonts_list = [6, 9, 2, 0, 7, 4, 8, 5, 3, 1 ]
    if "jeux_interdits" in name:
        gl.fonts_list = [4, 9, 3, 8, 6, 2]
    if "gaynor_i_will_survive" in name:
        gl.fonts_list = [6, 1, 2, 3, 4, 0, 9, 5]
    if "Dutronc_cactus" in name:
        gl.fonts_list = [5, 0, 6, 8] 


def get_channel():
    """16 channel maxi
    channel 9 pour drums
    Les channels sont attribués dans l'ordre des instruments de la liste
    """

    channels = []
    channels_no_drum = [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16]
    nbr = 0
    for instrument in gl.instruments:
        if not instrument[1]:  # instrument[1] = boolean
            channels.append(channels_no_drum[nbr])
            nbr += 1
            if nbr > 14: nbr = 0
        else:
            channels.append(10)

    return channels


def init_midi():
    """Pour jouer les json en midi

    bank = 0
    bank_number = instrument[]
    Dans PlayOneMidiPartition, une note est jouée avec:
        .thread_play_note(note, volume)
    La note est stoppée si:
        objet.thread_dict[(note, volume)] = 0

    gl.instruments = [[[0, 25], false, "Bass"], [[0, 116], true, "Drums2"]]
        instrum = [[0, 25], false, "Bass"]
    """

    fonts = gl.conf["music_and_letters"]["fonts"]
    channels = get_channel()

    # Création d'un dict des objets pour jouer chaque instrument
    gl.instruments_player = {}

    # Limitation du nombre d'instruments
    n = len(gl.instruments)
    if n > 10: n = 10
    for i in range(n):
        instrum = gl.instruments[i]
        chan = channels[i]
        is_drum = instrum[1]
        bank = instrum[0][0]
        bank_number = instrum[0][1]
        gl.instruments_player[i] = OneInstrumentPlayer(fonts, chan, bank,
                                                       bank_number)


def intro_init():
    # Phases du jeu "intro" "music and letters" "get shot"
    gl.phase = "intro"


def music_and_letters_init():
    get_conf()
    set_variable()
    set_tempo()
    get_midi_json()
    sleep(1)
    init_midi()
    sleep(1)
    gl.phase = "music and letters"
    gl.size_min = gl.conf["music_and_letters"]["size_min"]
    gl.size_max = gl.conf["music_and_letters"]["size_max"]


def get_shot_init():
    create_directories()
    get_get_shot_json()
    # Pas de shuffle des polices, elles y passent toutes
    gl.fonts_list = []
    for i in range(10):
        gl.fonts_list.append(i)

    # Fond de l'image pour get shot
    # possible: noir ou brouillard ou video":
    gl.fond = gl.conf["letters_shot"]["fond"]
    if gl.fond == "video":
        set_video()
        
    gl.phase = "get shot"
    
    # letters shot
    gl.nombre_shot_total = gl.conf['letters_shot']['nombre_shot_total']
    gl.shot_size = gl.conf["letters_shot"]["shot_size"]

    gl.size_min = gl.conf["letters_shot"]["size_min"]
    gl.size_max = gl.conf["letters_shot"]["size_max"]
    gl.scale = gl.conf["letters_shot"]["letters_scale"]
        
    # Pour occurence avec get shot
    gl.comptage = {}

    l = "abcdefghijklmnopqrstABCDEFGHIJKLMNOPQRST"
    letters = list(l)
    for i in range(10):
        gl.comptage[i] = {}
        for l in letters:
            gl.comptage[i][l] = 0
    gl.tempo['shot'].reset()
    print("\n\nInitialisation de get_shot\n")


def get_sun_set():
    gl.sun_energy_min = float(gl.conf["blend"]["sun_energy_min"])
    gl.sun_energy_max = float(gl.conf["blend"]["sun_energy_max"])
    gl.sun_color_min = float(gl.conf["blend"]["sun_color_min"])
    gl.sun_color_max = float(gl.conf["blend"]["sun_color_max"])


def write_instruments_text():
    """gl.instruments = [[[0, 39], false, ''],
                        [[0, 62], false, ''],
                        [[0, 74], false, ''],
                        [[0, 82], false, ''],
                        [[0, 32], false, ''],
                        [[0, 63], false, ''],
                        [[8, 117], true, ''],
                        [[0, 87], false, ''],
                        [[0, 53], false, ''],
                        [[0, 34], false, '']]
        à traduire dans
            gl.midi_json.txt
        data = "0 39\n0 62\n....."

        
    """

    data = ""
    
    for i in range(len(gl.instruments)):
        # [[0, 39], false, ''] --> 0 39
        # Fonts par instrument
        # gl.fonts_list[i]
        
        bank = str(gl.instruments[i][0][0])
        instr = str(gl.instruments[i][0][1])
        police = str(gl.fonts_list[i])
        data += bank + " " + instr + " " + police + "\n"
        
    fichier = gl.music_to_shot_sub_directory + "/instruments.txt"

    # Ecriture
    gl.tools.write_data_in_file(data, fichier, "w")
    print("Fichier créé:", fichier)


def create_music_to_shot_subdirectories(name):
    """Création du ou des sous répertoires"""
    
    gl.music_to_shot_sub_directory = gl.music_to_shot_directory + "/" + name
    gl.tools.create_directory(gl.music_to_shot_sub_directory)
    
    # Fichier text
    write_instruments_text()

        
def get_midi_json():
    """
    json_data = {"partitions":  [partition_1, partition_2 ......],
                 "instruments": [instrument_1.program,
                                 instrument_2.program, ...]
    """

    if gl.phase == "music and letters":
        gl.nbr = gl.conf["music_and_letters"]["file_nbr"]
        js = gl.conf["music_and_letters"]["json_files"]
        gl.tempo["cube"].reset()
        
    if gl.phase == "music to shot":
        js = gl.conf["play_letters_shot"]["json_files"]

    all_json = gl.tools.get_all_files_list(js, ".json")
    # Tri des json alpha
    all_json = sorted(all_json)
    
    if gl.phase == "music and letters":
        # Reset de gl.nbr si fini
        if gl.nbr >= len(all_json):
            gl.nbr = 0
            
    if gl.phase == "music to shot":
        gl.nbr += 1
        if all_json == []:
            print("Pas de fichier json à convertir en images")
            os._exit(0)
        if gl.nbr == len(all_json):
            print("Fin des conversions")
            sleep(1)
            os._exit(0)
            
    gl.midi_json = all_json[gl.nbr]

    name = gl.midi_json.split("/")[-1]
    print("\n    Fichier en cours", name[:-5], "\n")
    
    # Enregistrement du numéro du prochain fichier à lire
    if gl.phase == "music and letters":
        section = "music_and_letters"
        gl.ma_conf.save_config(section, "file_nbr", gl.nbr + 1)

    # Lecture du json
    with open(gl.midi_json) as f:
        data = json.load(f)
    f.close()
    
    gl.partitions = data["partitions"]  # [partition_1, partition_2 ..
    gl.instruments = data["instruments"]  # [instrument_1.program, ...
    gl.partition_nbr = len(gl.partitions)

    # Vérification d'un json valide
    if not len(gl.partitions) > 0:
        print("Json non valide:", name)
        os._exit(0)
        
    # Pour choix 2 et 3
    fonts_shuffle(name)

    # Sous dossiers et fichier texte
    if gl.phase == "music to shot":
        create_music_to_shot_subdirectories(name[:-5])
        
    print("Nombre d'instrument:", len(gl.instruments))
    for instr in gl.instruments:
        if instr[1]:
            drum = "Drum"
        else:
            drum = ""
        print('    Bank: {:>1} Number: {:>3} {:>6}  Name: {:>16}'.\
                   format(instr[0][0], instr[0][1], drum, instr[2]))
    print("\n")

    
def music_to_shot_init():
    
    # Reload de la conf
    get_conf()

    print("Nouveau json à convertir en image:")
    
    set_variable()
    
    # Dossiers des images
    gl.music_to_shot_directory = gl.conf["play_letters_shot"]["pl_shot"]
    gl.tools.create_directory(gl.music_to_shot_directory)

    gl.phase = "music to shot"
    
    # Play letters shot
    gl.nombre_shot_total = gl.conf['play_letters_shot']['nombre_shot_total']
    gl.shot_size = gl.conf["play_letters_shot"]["shot_size"]

    gl.size_min = gl.conf["play_letters_shot"]["size_min"]
    gl.size_max = gl.conf["play_letters_shot"]["size_max"]
    gl.scale = gl.conf["play_letters_shot"]["letters_scale"]

    # Fond de l'image pour get shot
    # possible: noir ou brouillard ou video":
    gl.fond = gl.conf["play_letters_shot"]["fond"]
    
    get_midi_json()

    if gl.fond == "video":
        set_video()

    
def main():
    """Lancé une seule fois à la 1ère frame au début du jeu par main_once."""

    print("Initialisation des scripts lancée un seule fois au début du jeu:")

    # Le couteau suisse
    gl.tools = MyTools()

    # Récupération de la configuration
    get_conf()
    set_variable()
    gl.nbr = -1
    set_tempo()
    get_sun_set()

    # Numéro de toutes les lettres entre 0 et 399
    get_obj_num()

    # Carrés en dehors de la vue caméra
    set_all_letters_position()

    intro_init()

    # Pour les mondoshawan
    print("Initialisation du jeu terminée\n\n")
