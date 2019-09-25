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
    - yolov3.cfg
    - yolov3_best.weights
    - obj.data
sont à définir dans letters.ini
"""


import os, sys
import time
import re
import textwrap
import cv2
import numpy as np
import darknet
from random import randint

# Import du dossier parent soit letters
# Pas d'import possible direct du dossier parent
# ValueError: attempted relative import beyond top-level package

sys.path.append("..")
from letters_path import LettersPath

lp = LettersPath()
letters_dir = lp.letters_dir
CONF = lp.conf
shot_control_dir = lp.shot_control_dir

sys.path.append(lp.get_midi_directory())
from analyse_play_midi import OneInstrumentPlayer

from pymultilame import MyConfig, MyTools


JSON_TO_IMAGE = "../json_to_image/cougourdoun-nicola"


class YOLO:

    def __init__(self):
        self.mt = MyTools()
        self.loop = 1

        # Initialisation de la détection
        self.set_darknet()

        # Paramètres de détections
        self.thresh = int(CONF['darknet']['thresh'])
        self.hier_thresh = int(CONF['darknet']['hier_thresh'])
        self.nms = int(CONF['darknet']['nms'])

        # Trackbars
        self.create_trackbar()
        self.set_init_tackbar_position()

        # Midi
        self.fonts = CONF['midi']['fonts']
        self.set_canaux()
        self.player = {}
        self.set_players()

    def set_darknet(self):
        configPath = CONF['darknet']['configpath']
        weightPath = CONF['darknet']['weightpath']
        metaPath = CONF['darknet']['metapath']

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
                
        # Create an image we reuse for each detect
        self.darknet_image = darknet.make_image(\
                                        darknet.network_width(self.netMain),
                                        darknet.network_height(self.netMain),
                                        3)

    def set_canaux(self):
        """Définit les canaux avec le fichier texte
        0 39
        0 62
        ...
        """
        self.canaux = []

        file_name = JSON_TO_IMAGE + "/instruments.txt"
        data = self.mt.read_file(file_name)
        lines = data.splitlines()
        for line in lines:
            line_list = line.split(" ")
            self.canaux.append(line_list)
                    
    def set_players(self):
        """Crée les players pour chaque canal"""
        
        for i in range(len(self.canaux)):
            # Les drums ne sont pas sur le channel,
            # complique et sert à rien
            channel = i
            bank = int(self.canaux[i][0])
            bank_number = int(self.canaux[i][1])
            self.player[i] = OneInstrumentPlayer(self.fonts,
                                                 channel,
                                                 bank,
                                                 bank_number)
        print("Nombre de player:", len(self.player))
            
    def play_notes(self, notes):
        """[(note, volume, police), ...] = [(45, 124, 2), ... ]"""

        notes_en_cours = []
        for note in notes:
            #if note[2] < 9:
            notes_en_cours.append([note[0], note[2]])

        # Stop des notes en cours et absentes de notes
        for i in range(len(self.player)):
            for key, val in self.player[i].thread_dict.items():
                if (key, i) not in notes_en_cours:
                    self.player[i].thread_dict[key] = 0

        # play des nouvelles notes
        for note in notes:
            if 0 < note[0] < 127:
                if 0 < note[2] < len(self.canaux):
                    print(note[2], note[0])
                    if not self.player[note[2]].thread_dict[note[0]]:
                        vol = note[1]
                        if vol < 50: vol = 100
                        self.player[note[2]].thread_play_note(note[0], vol)

    def create_trackbar(self):
        """
        thresh            min 0 max 1
        hier_thresh       min 0 max 1
        nms               min 0 max 1
        """
        cv2.namedWindow('Reglage')
        self.reglage_img = np.zeros((10, 1000, 3), np.uint8)

        cv2.createTrackbar('threshold', 'Reglage', 0, 100, self.onChange_thresh)
        cv2.createTrackbar('hier_thresh', 'Reglage', 0, 100, self.onChange_hier_thresh)
        cv2.createTrackbar('nms', 'Reglage', 0, 100, self.onChange_nms)

    def set_init_tackbar_position(self):
        """setTrackbarPos(trackbarname, winname, pos) -> None"""

        cv2.setTrackbarPos('threshold', 'Reglage', self.thresh)
        cv2.setTrackbarPos('hier_thresh', 'Reglage', self.hier_thresh)
        cv2.setTrackbarPos('nms', 'Reglage', self.nms)

    def onChange_thresh(self, thresh):
        """min=1 max=100 step=1 default=0.5"""
        if thresh == 0: thresh = 5
        if thresh == 100: thresh = 95
        self.thresh = int(thresh)
        self.save_change('darknet', 'thresh', self.thresh)

    def onChange_hier_thresh(self, hier_thresh):
        """min=1 max=100 step=1 default=0.5"""
        if hier_thresh == 0: hier_thresh = 5
        if hier_thresh == 100: hier_thresh = 95
        self.hier_thresh = int(hier_thresh)
        self.save_change('darknet', 'hier_thresh', self.hier_thresh)

    def onChange_nms(self, nms):
        """min=1 max=100 step=1 default=0.5"""
        if nms == 0: nms = 5
        if nms == 100: nms = 95
        self.nms = int(nms)
        self.save_change('darknet', 'nms', self.nms)

    def save_change(self, section, key, value):
        lp.save_config(section, key, value)

    def get_sorted_shot_list(self):

        fli = self.mt.get_all_files_list(JSON_TO_IMAGE, ".jpg")

        shot_list = [0]*len(fli)
        for image in fli:
            # ../json_to_image/s_j_to_i_2677.jpg s_j_to_i_2677.jpg
            nbr = image.split("/")[-1].split("_")[-1][:-4]  # 2677
            shot_list[int(nbr)-60] = image

        return shot_list

    def detect(self):
        """FPS = 162 sur MSI sans détection: lecture + affichage = 6 ms"""

        shot_list = self.get_sorted_shot_list()
        i = 0
        fps = 0
        print("Nombre d'images:", len(shot_list))
        t_init = time.time()

        while self.loop:
            name = shot_list[i]
            i += 1
            fps += 1
            ta = time.time()
            if ta > t_init + 1:
                print("FPS =", fps)
                t_init = time.time()
                fps = 0

            # Capture des positions des sliders
            self.thresh = cv2.getTrackbarPos('threshold','Reglage')
            self.hier_thresh = cv2.getTrackbarPos('hier_thresh','Reglage')
            self.nms = cv2.getTrackbarPos('nms','Reglage')

            img = cv2.imread(name)

            img_resized = cv2.resize(img, (darknet.network_width(self.netMain),
                                           darknet.network_height(self.netMain)),
                                           interpolation=cv2.INTER_LINEAR)

            darknet.copy_image_from_bytes(self.darknet_image, img_resized.tobytes())

            detections_l = darknet.detect_image(self.netMain,
                                                self.metaMain,
                                                self.darknet_image,
                                                self.thresh/100,
                                                self.hier_thresh/100,
                                                self.nms/100)

            # Application des détections dan sl'image
            image, letters = cvDrawBoxes(detections_l, img_resized)

            notes = letters_to_notes(letters)
            self.play_notes(notes)

            image = cv2.resize(image, (800, 800), interpolation=cv2.INTER_LINEAR)
            # Affichage du Semaphore
            cv2.imshow('Letters', image)
            # Affichage des trackbars
            cv2.imshow('Reglage', self.reglage_img)

            # Attente
            k = cv2.waitKey(1)
            if i == len(shot_list) :
                self.loop = 0
            # Echap pour quitter
            if k == 27:
                self.loop = 0

        cv2.destroyAllWindows()


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
        notes = [(note, volume, police), ...] = [(45,124, 2), ... ]

    notes_d[police] = [ 10+5, 100+20+4]

    """

    notes = []
    notes_d = {}

    # Parcours des 10 polices possibles
    for i in range(10):
        notes_d[i] = [0, 0]
        for letter in letters:
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
            notes.append([v[0], v[1], k])

    return notes


def put_text(img, text, xy, size, thickness):
    """img=cv.putText(img, text, org, fontFace, fontScale,
                      color[, thickness[, lineType[, bottomLeftOrigin]]])
    """

    cv2.putText(img,
                text,
                (xy[0], xy[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                size,
                [0, 255, 255],
                thickness,
                cv2.LINE_AA)


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
        print(detection)
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
            #                color[, thickness[, lineType[, bottomLeftOrigin]]])
            cv2.putText(img,
                        t,
                        (pt1[0], pt1[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        [0, 255, 0],
                        1)

    return img, letters


def crop(img):
    """
    Coupe les 2 cotés pour avoir une image carrée
    à partir de l'image de la cam:
    x = int((a - b)/2)
    y = 0
    frame = frame[y:y+h, x:x+w]
    """

    a = img.shape[1]  # 640
    b = img.shape[0]  # 480
    # A couper de chaque coté
    c = abs(int((a - b)/2))

    return img[0:b, c:c+b]


if __name__ == "__main__":

    # #note = 123
    # #casse = "min"
    # #c, d, u = conversion(note, casse)
    # #print(c, d, u)
    # #f = "5"

    # #letters = []
    # #for l in [c, d, u]:
        # #if l:
            # #a = "font_" + f + "_" + l
            # #print(a)
            # #letters.append(a)

    # #print("letters", letters)
    # #letters_to_notes(letters)

    yolo = YOLO()
    yolo.detect()
