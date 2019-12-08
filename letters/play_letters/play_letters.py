#!python3
# -*- coding: UTF-8 -*-

"""
Reconnaissance de lettres dans une image

La lib
        libdarknet.so
doit être dans le dossier darknet de letters,
elle est créée à la compilation des sources de darknet
et se trouve dans ce dossier.

Les fichiers:
    configpath
    weightpath
    metapath
sont à définir dans letters.ini

Définir aussi:
[benchmark]
[essai]
qui indicie le json de sortie avec toutes les notes jouées.
"""


import os, sys
import subprocess
import gc
import time
import re
import textwrap
import cv2
import numpy as np
import darknet
from random import randint, shuffle
import json

# Import du dossier parent soit letters
# Pas d'import possible direct du dossier parent
# ValueError: attempted relative import beyond top-level package
sys.path.append("..")
from letters_path import LettersPath
lp = LettersPath()
letters_dir = lp.letters_dir
sys.path.append(lp.get_midi_directory())

from analyse_play_midi import OneInstrumentPlayer
from pymultilame import MyConfig, MyTools


class YOLO:

    def __init__(self, images_directory, essai, save, test=0, weights=""):
        """
        essai = numéro del'eaasi dans ini
        save = sauvegarde des notes en json
        test = bidouilles pour passer une série de weights
        """

        # Mes outils
        self.mt = MyTools()

        self.lp = LettersPath()
        self.CONF = self.lp.conf
        self.essai = essai
        self.save = save
        self.test = test

        self.weights = weights
        if self.weights:
            print("Fichier de poids utilisé:", self.weights)
        self.get_weights_file_indice()
        if self.weights:
            self.create_test_subdir()

        # Paramètres de la conf
        # Avec ou sans GPU
        self.gpu = self.CONF['play_letters']['gpu']
        # Résolution de l'écran ou du VP: x, y
        self.screen = self.CONF['play_letters']['screen']

        # Boucle opencv
        self.loop = 1
        self.fps = 0

        # Récup des images
        self.images_directory = images_directory
        self.shot_list = self.get_sorted_shot_list()
        self.all_shot = self.get_all_shot()

        # nom du morceau
        self.filename = self.images_directory.split("/")[-1]

        # Initialisation de la détection
        self.set_darknet()

        # Paramètres de détections
        self.thresh = int(self.CONF['play_letters']['thresh'])
        self.hier_thresh = int(self.CONF['play_letters']['hier_thresh'])
        self.nms = int(self.CONF['play_letters']['nms'])

        # Windows
        self.create_windows()

        # Trackbars
        self.create_trackbar()
        self.set_init_tackbar_position()

        # Midi
        self.fonts = self.CONF['music_and_letters']['fonts']
        self.instruments = []
        self.get_instruments()
        self.notes_en_cours = []
        self.players = {}
        self.set_players()
        self.all_notes = []

    def create_windows(self):
        cv2.namedWindow('Reglage')
        cv2.moveWindow('Reglage', 0, 25)
        self.fullscreen = self.CONF['play_letters']['fullscreen']
        if self.fullscreen:
            cv2.namedWindow('Letters', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(  'Letters',
                                    cv2.WND_PROP_FULLSCREEN,
                                    cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow('Letters')
            cv2.moveWindow('Letters', 0, 25)
        self.titre = 0
        b = int(416*self.screen[0]/self.screen[1])
        self.black_image = np.zeros((416, b, 3), np.uint8)

    def get_weights_file_indice(self):
        """Uniquement pour test
        weightpath =
        ../darknet/data_22/backup/yolov3-tiny_3l_22_best.weights
        début = ../darknet/data_22/backup/yolov3-tiny_3l_22_
        fin = .weights
        """

        a = len("/media/data/projets/darknet-letters/letters/darknet/data_22/backup/yolov3-tiny_3l_22_")
        b = len(".weights")
        indice = str(self.weights[a:-b])

        return indice

    def create_test_subdir(self):
        doss = "/media/serge/BACKUP/play_letters_shot/pl_shot_14_jpg/test/"
        for i in range(43):
            directory = doss + str((i+1) * 1000)
            self.mt.create_directory(directory)

    def set_darknet(self):
        """Si weight_influence_test,
        teste tous les
        yolov3-tiny_3l_22_xxxxxxx.weights
        du dossier backup

        free_network = lib.api_free_network
        free_network.argtypes = [c_void_p]

        adapté à ce script:
        free_network = darknet.lib.api_free_network
        free_network.argtypes = [c_void_p]
        """

        configPath = self.CONF['play_letters']['configpath']

        if not self.test:
            weightPath = self.CONF['play_letters']['weightpath']
        else:
            weightPath = self.weights

        metaPath = self.CONF['play_letters']['metapath']

        self.netMain = darknet.load_net_custom(configPath.encode("ascii"),
                                                weightPath.encode("ascii"),
                                                0,
                                                1)
        self.metaMain = darknet.load_meta(metaPath.encode("ascii"))

        with open(metaPath) as metaFH:
            metaContents = metaFH.read()
            match = re.search("names *= *(.*)$", metaContents,
                              re.IGNORECASE | re.MULTILINE)
            if match:
                result = match.group(1)
            else:
                result = None
            try:
                if os.path.exists(result):
                    with open(result) as namesFH:
                        namesList = namesFH.read().strip().split("\n")
                        self.altNames = [x.strip() for x in namesList]
            except TypeError:
                print("Erreur self.altNames")

        if self.gpu:
            self.free_network = darknet.lib.api_free_network

        # Create an image we reuse for each detect
        self.darknet_image = darknet.make_image(\
                                        darknet.network_width(self.netMain),
                                        darknet.network_height(self.netMain),
                                        3)

    def get_instruments(self):
        """Récupère les infos de instruments.txt dans self.instruments."""

        file_name = self.images_directory + "/instruments.txt"
        data = self.mt.read_file(file_name)

        if data:
            lines = data.splitlines()
            for line in lines:
                line_list = line.split(" ")
                self.instruments.append(line_list)
        else:
            print("Pas de fichier txt donc pas d'instruments !")
            print("    Morceau suivant ....\n\n")
            self.instruments = None
            self.loop = 0

    def set_players(self):
        """Crée les players pour chaque canal
        Les drums ne sont pas sur le channel 9, complique et sert à rien

        la font i est sur le canal i
        for i in range(len(self.instruments)):
        self.instruments = [[0, 12, 5], [0, 0, 1]]
                            [bank,
                               bank_number = instrument,
                                                     font]
        """

        if self.instruments:
            i = 0
            for instrument in self.instruments:
                channel = int(instrument[2])
                bank = int(instrument[0])
                bank_number = int(instrument[1])
                self.players[channel] = OneInstrumentPlayer(self.fonts,
                                                        channel,
                                                        bank,
                                                        bank_number)
                i += 1

        print("Nombre de player:", len(self.players))

    def create_trackbar(self):
        """
        thresh            min 0 max 1
        hier_thresh       min 0 max 1
        nms               min 0 max 1
        """

        self.reglage_img = np.zeros((100, 600, 3), np.uint8)
        # #self.reglage_img = put_text(self.reglage_img,
                                    # #self.filename,
                                    # #(10, 50),
                                    # #size=0.8,
                                    # #thickness=2)

        cv2.createTrackbar('threshold_', 'Reglage', 0, 100,
                                            self.onChange_thresh)
        cv2.createTrackbar('hier_thresh', 'Reglage', 0, 100,
                                            self.onChange_hier_thresh)
        cv2.createTrackbar('nms_____', 'Reglage', 0, 100,
                                            self.onChange_nms)

    def set_init_tackbar_position(self):
        """setTrackbarPos(trackbarname, winname, pos) -> None"""

        cv2.setTrackbarPos('threshold_', 'Reglage', self.thresh)
        cv2.setTrackbarPos('hier_thresh', 'Reglage', self.hier_thresh)
        cv2.setTrackbarPos('nms_____', 'Reglage', self.nms)

    def onChange_thresh(self, thresh):
        """min=1 max=100 step=1 default=0.5"""
        if thresh == 0: thresh = 5
        if thresh == 100: thresh = 95
        self.thresh = int(thresh)
        self.save_change('play_letters', 'thresh', self.thresh)

    def onChange_hier_thresh(self, hier_thresh):
        """min=1 max=100 step=1 default=0.5"""
        if hier_thresh == 0: hier_thresh = 5
        if hier_thresh == 100: hier_thresh = 95
        self.hier_thresh = int(hier_thresh)
        self.save_change('play_letters', 'hier_thresh', self.hier_thresh)

    def onChange_nms(self, nms):
        """min=1 max=100 step=1 default=0.5"""
        if nms == 0: nms = 5
        if nms == 100: nms = 95
        self.nms = int(nms)
        self.save_change('play_letters', 'nms', self.nms)

    def save_change(self, section, key, value):
        lp.save_config(section, key, value)

    def get_sorted_shot_list(self):

        images = self.mt.get_all_files_list(self.images_directory, ".jpg")

        shot_list = [0]*len(images)

        # Récup du numéro le plus petit, les numéros ensuite se suivent
        mini = 10000000
        for image in images:
            nbr = int(image.split("/")[-1].split("_")[-1][:-4])
            if nbr < mini:
                mini = nbr

        # Tri des images
        n = 0
        for image in images:
            # Si de 500 à 1500
            # ../play_letters/s_j_to_i_1243.jpg devient s_j_to_i_1243.jpg
            nbr = int(image.split("/")[-1].split("_")[-1][:-4])  # 1243
            shot_list[nbr - mini] = image

        return shot_list

    def get_all_shot(self):
        """Charge en mémoire toutes les images du dossiers à lire par l'IA"""

        print("\n\nChargement de toutes les images en RAM. Patience ...\n\n")

        all_shot = []
        for shot_file in self.shot_list:
            img = cv2.imread(shot_file)
            all_shot.append(img)

        return all_shot

    def notes_cleaning(self, notes):
        # Suppression des doublons
        clean_notes = []
        for note in notes:
            if note not in clean_notes:
                clean_notes.append(note)

        # Validation des notes
        new_notes = []
        for font, note, vol in notes:
            # self.instruments = [[0, 12, 5], [0, 0, 1]]
            all_fonts = []
            for inst in self.instruments:
                all_fonts.append(int(inst[2]))
            if font not in all_fonts:
                font = None

            # note 1 à 127
            if note < 1 or note > 127:
                note = None

            # ## Volume 0 à 127:
            # #if vol > 127: vol = 127
            # #if vol < 0: vol = 0
            # Le volume est forcé à 127
            vol = 127

            if font is not None:
                if note:
                    new_notes.append([font, note, vol])

        return new_notes

    def play_notes(self, notes):
        """new_notes = [(police, note, volume), ...] = [(5, 124, 127), ... ]
        la police n'est pas le player
        self.players[i].thread_dict[key] = 0
        """

        new_notes = self.notes_cleaning(notes)

        # Notes en en_cours ******************************************
        en_cours = []
        # key=note, val=thread en cours 0 ou 1
        for k, v in self.players.items():
            for key, val in self.players[k].thread_dict.items():
                if val != 0:
                    en_cours.append((k, key))
        # #print("en_cours:", en_cours)

        # Fin des notes qui ne sont plus en en_cours *****************
        # notes = [(player, note, volume), ...]
        # en_cours = [(player, note), ... ]
        for ec in en_cours:
            player, note = ec
            ssss = [player, note, 127]  # list et non tuple !!
            if ssss not in new_notes:
                self.players[player].thread_dict[note] = 0
                # #print("Fin de:", player, note)

        # Lancement des nouvelles notes ******************************
        for player, note, vol in new_notes:
            if (player, note) not in en_cours:
                # #print("nouvelle", player, note)
                self.players[player].thread_play_note(note, 127)  # vol)

    def save_all_notes(self):
        """
        /bla...bla/play_letters_shot_jpg_3/bob_sheriff
        to
        /bla...bla/play_letters_shot_jpg_3/bob_sheriff_data.json
        """

        if not self.weights:
            json_name = self.images_directory + "_" + str(self.essai) + ".json"
        else:
            # Bidouille non générale
            a = len("/media/serge/BACKUP/play_letters_shot/pl_shot_14_jpg/")
            name = self.images_directory[a:] + "_"
            # les fichiers sont dans 1 sous dossier indice
            indice = str(self.get_weights_file_indice())
            doss = "/media/serge/BACKUP/play_letters_shot/pl_shot_14_jpg/test/"
            json_name = doss + indice + "/" + name + str(self.essai) + ".json"

        with open(json_name, 'w') as f_out:
            json.dump(self.all_notes, f_out)
        f_out.close()
        print('Enregistrement de:', json_name)

    def put_titre(self, image):
        """Insère le titre si i"""

        if self.titre:
            filename = self.filename
            filename = filename.replace("f_", "")
            filename = filename.replace("_", " ")
            filename = filename.replace("-", " ")
            image = put_text(   image,
                                filename,
                                (10, 50),
                                size=0.5,
                                thickness=1)
        return image

    def apply_k(self, k, i):
        # Space pour morceau suivant et attente
        if k == 32:
            self.loop = 0

        # Affichage du titre si "i"
        if k == ord('i'):  # 105:
            if not self.titre:
                self.titre = 1
            else:
                self.titre = 0

        # Echap pour finir le script python
        if k == 27:
            os._exit(0)

        # Gestion de la fin du morceaux
        if i == len(self.shot_list) :
            self.loop = 0

    def detect(self):
        """FPS = 40 sur GTX1060"""

        i = 0
        fps = 0
        t_init = time.time()
        tempo = 1
        t_tempo = time.time()

        # Si pas d'image, on passe la boucle
        if not self.all_shot:
            self.loop = 0

        while self.loop:
            #black_image = self.black_image.copy()
            # Récup d'une image
            img = self.all_shot[i]

            # ## Capture des positions des sliders
            # #self.thresh = cv2.getTrackbarPos('threshold_','Reglage')
            # #self.hier_thresh = cv2.getTrackbarPos('hier_thresh','Reglage')
            # #self.nms = cv2.getTrackbarPos('nms','Reglage')

            # #img_resized = cv2.resize(img,
                                    # #(darknet.network_width(self.netMain),
                                     # #darknet.network_height(self.netMain)),
                                     # #interpolation=cv2.INTER_LINEAR)

            darknet.copy_image_from_bytes(self.darknet_image,
                                          img.tobytes())

            detections_l = darknet.detect_image(self.netMain,
                                                self.metaMain,
                                                self.darknet_image,
                                                self.thresh/100,
                                                self.hier_thresh/100,
                                                self.nms/100)

            # Application des détections dans l'image
            image, letters = cvDrawBoxes(detections_l, img)
            notes = letters_to_notes(letters)
            self.play_notes(notes)

            # Ajout des notes pour enregistrement à la fin
            if self.save:
                self.all_notes.append(notes)

            # Insertion du titre
            image = self.put_titre(image)

            if not self.fullscreen:
                img = cv2.resize(image, (850, 850),
                                 interpolation=cv2.INTER_LINEAR)
            else:
                # gray[y1:y2, x1:x2] 162:578
                # 1440/900 = 1.6
                # #a = (self.screen[0]/self.screen[1] -1) / 2
                # #x1 = int(a*416)
                # #x2 = x1 + 416
                # #y1 = 0
                # #y2 = 416
                # #black_image[y1:y2, x1:x2] = image
                img = image  # black_image
                img = put_text( img,
                                  str(self.fps),
                                  (10, 100),
                                  size=0.5,
                                  thickness=1)

            # Affichage
            cv2.imshow('Letters', img)  # image)
            # Affichage des trackbars
            cv2.imshow('Reglage', self.reglage_img)

            # Comptage
            i += 1  # prochaine image
            fps += 1
            ta = time.time()

            # Pour fps = 40 soit ta - t_tempo = 0.025
            # 0.035 pour fps = 40, 0.052 pour fps = 30
            tempo = int(1000 * (0.052 - (ta - t_tempo)))
            if tempo < 1:
                tempo = 1
            t_tempo = ta

            if ta > t_init + 1:
                self.fps = fps
                # #print("FPS =", round(fps, 1))
                t_init = time.time()
                fps = 0

            k = cv2.waitKey(tempo)
            self.apply_k(k, i)

        cv2.destroyAllWindows()

        # Libération de la mémoire GPU
        if self.gpu:
            self.free_network(self.netMain)

        # Delete images
        del self.all_shot

        # Enregistrement des notes
        if self.save:
            self.save_all_notes()

        # Fin des fluidsynth
        for k,v in self.players.items():
            self.players[k].stop_audio()
        time.sleep(0.3)


CONVERSION = {  "b": 1,
                "c": 2,
                "d": 3,
                "e": 4,
                "f": 5,
                "g": 6,
                "h": 7,
                "i": 8,
                "j": 9,
                "k": 10,
                "l": 20,
                "m": 30,
                "n": 40,
                "o": 50,
                "p": 60,
                "q": 70,
                "r": 80,
                "s": 90,
                "t": 100,
                "B": 1,
                "C": 2,
                "D": 3,
                "E": 4,
                "F": 5,
                "G": 6,
                "H": 7,
                "I": 8,
                "J": 9,
                "K": 10,
                "L": 20,
                "M": 30,
                "N": 40,
                "O": 50,
                "P": 60,
                "Q": 70,
                "R": 80,
                "S": 90,
                "T": 100}


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
    Les a et A ne sont pas utilisés, donc 380 objets différents.
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


def letters_to_notes(letters):
    """
    letters:
        toutes les notes de l'image = ["font_0_b", "font_1_l"]

    Retourne les notes en clair:
        notes = [[player, note, vol], ...] = [(45,124, 2), ... ]

    notes_d[police] = [ 10+5, 100+20+4]
    """

    notes = []
    notes_d = {}

    # Parcours des 10 polices possibles
    for i in range(10):
        notes_d[i] = [0, 0]
        for letter in letters:
            # le 5ème de "font_0_b" est la font
            police = int(letter[5])
            if police == i:
                l = letter[7]
                x = CONVERSION[l]
                if l.islower():
                    notes_d[i][0] += x
                else:
                    notes_d[i][1] += x

    for k, v in notes_d.items():
        if v[0] != 0:
            notes.append([k, v[0], 127])  # v[1]])

    return notes


def put_text(img, text, xy, size, thickness):
    """img=cv.putText(img, text, org, fontFace, fontScale,
                      color[, thickness[, lineType[, bottomLeftOrigin]]])
    """

    img = cv2.putText(img,
                        text,
                        (xy[0], xy[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        size,
                        [0, 255, 255],
                        thickness,
                        cv2.LINE_AA)
    return img


def convertBack(x, y, w, h):
    """
    Permet d'avoir le rectangle dans l'image affichée.
    """

    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img):
    """Construit le rectangle autour des détections
    Une détection
        b'font_9_K', 0.995, (74.0, 245.0, 40.6, 39.6))
    """
    letters = []
    for detection in detections:
        # La lettre détectée
        lettre = detection[0].decode("utf-8")

        if "font_" in lettre:
            # Ajout à la liste des lettres
            letters.append(lettre)

            x, y, w, h = detection[2][0],\
                            detection[2][1],\
                            detection[2][2],\
                            detection[2][3]
            xmin, ymin, xmax, ymax = convertBack(float(x), float(y),
                                                 float(w), float(h))
            pt1 = (xmin, ymin)
            pt2 = (xmax, ymax)
            cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
            # + " [" + str(round(detection[1] * 100, 2)) + "]"
            t = lettre[5:]
            # img=cv.putText(img, text, org, fontFace, fontScale,
            #              color[, thickness[, lineType[, bottomLeftOrigin]]])
            cv2.putText(img,
                        t,
                        (pt1[0], pt1[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        [0, 255, 0],
                        1)

    return img, letters


def play_letters(dossier, essai, save, test, weights):
    """Joue les sous-dossiers du dossier"""

    sd_list = [x[0] for x in os.walk(dossier)]

    # Trié ou pas
    if CONF["play_letters"]["sorted"]:
        sd_list = sorted(sd_list)
    else:
        shuffle(sd_list)
        
    # Pas le dossier principal
    sd_list.remove(dossier)

    # Récup du dernier précédent au lancement
    file_nbr = CONF["play_letters"]["file_nbr"]

    while 1:
        sd = sd_list[file_nbr]

        # Enregistrement du numéro du prochain fichier
        file_nbr += 1
        if file_nbr >= len(sd_list):
            file_nbr = 0
        lp.save_config("play_letters", "file_nbr", file_nbr)

        yolo = YOLO(sd, essai, save, test, weights)
        yolo.detect()
        del yolo

    print("Done")


def test(dossier, essai):
    """
    best = 41000
    last = 43000
    final = 42000
    """
    mt = MyTools()

    w_dir = "/media/data/projets/darknet-letters/letters/darknet/data_22/backup/"
    w_list = mt.get_all_files_list(w_dir, ".weights")
    #print("\n\nTous les fichiers de poids:", w_list)

    for w in w_list:
        # Pas le dossier principal
        if w:
            print("\n\nFichier de poids en cours:", w, "\n\n")
        if w != w_dir:
            play_letters(dossier, essai, test=1, weights=w)


if __name__ == "__main__":

    CONF = lp.conf

    # Dossier des dossiers des images à convertir en musique
    dossier = CONF["play_letters_shot"]["pl_shot"] + "_jpg"

    # Définir le numéro de l'essai, utilisé dans le benchmark
    essai = CONF["benchmark"]["essai"]

    test = 0
    save = 0
    play_letters(dossier, essai, save, test, "")

    # #test(dossier, essai)

    os._exit(0)
