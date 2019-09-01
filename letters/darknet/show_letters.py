#!python3
# -*- coding: UTF-8 -*-


"""
Reconnaissance de lettres dans une image

La lib
        libdarknet.so
doit être dans le dossier darknet de letters,
elle est créée à la compilation des sources de darknet
et se trouve dans ce dossier. 
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


SHOT_JPG = "../json_to_image"

# Pour test
LETTERS = [ ['font_5_t', 'font_8_c', 'font_5_b', 'font_0_k', 'font_6_o', 'font_0_f', 'font_8_m', 'font_3_f', 'font_1_g', 'font_9_s', 'font_7_q', 'font_2_c', 'font_1_p', 'font_6_h', 'font_4_j', 'font_7_g', 'font_4_l', 'font_4_J', 'font_2_l', 'font_5_k', 'font_3_r'],
            ['font_7_S', 'font_2_R', 'font_7_B', 'font_6_L', 'font_4_I', 'font_8_T', 'font_8_C', 'font_5_O', 'font_6_H', 'font_2_C', 'font_9_R', 'font_2_c', 'font_1_B'],
            ['font_2_t', 'font_1_t', 'font_3_t', 'font_8_m', 'font_6_q', 'font_5_p', 'font_6_e', 'font_3_f', 'font_8_d', 'font_4_b', 'font_2_c', 'font_9_l', 'font_0_o', 'font_7_f', 'font_5_f', 'font_3_k', 'font_9_d', 'font_0_d', 'font_1_k'],
            ['font_6_Q', 'font_9_R', 'font_4_T', 'font_0_H', 'font_2_E', 'font_1_N', 'font_8_F', 'font_2_S', 'font_7_L', 'font_1_B', 'font_7_G', 'font_3_O', 'font_9_E', 'font_0_T', 'font_7_T', 'font_8_R', 'font_4_j', 'font_8_e', 'font_4_J'],
            ['font_9_t', 'font_5_n', 'font_3_o', 'font_3_f', 'font_1_e', 'font_7_n', 'font_2_d', 'font_6_o', 'font_8_t', 'font_8_g', 'font_0_k', 'font_7_e', 'font_1_n', 'font_9_l', 'font_4_g', 'font_9_h', 'font_2_n', 'font_6_g'],
            ['font_9_Q', 'font_6_L', 'font_7_T', 'font_5_K', 'font_4_B', 'font_8_T', 'font_8_G', 'font_1_I', 'font_9_I', 'font_7_K', 'font_3_H', 'font_4_R', 'font_5_I', 'font_0_L', 'font_3_O', 'font_6_I', 'font_1_s'],
            ['font_4_e', 'font_9_q', 'font_6_b', 'font_1_e', 'font_3_i', 'font_8_d', 'font_7_t', 'font_5_i', 'font_5_q', 'font_2_f', 'font_0_c', 'font_4_k', 'font_8_r', 'font_7_h', 'font_9_b', 'font_0_t', 'font_6_r'],
            ['font_5_G', 'font_3_D', 'font_6_D', 'font_0_D', 'font_7_J', 'font_5_R', 'font_8_Q', 'font_1_D', 'font_8_E', 'font_7_Q', 'font_2_P', 'font_6_S', 'font_4_E', 'font_3_O', 'font_4_P'],
            ['font_7_m', 'font_5_i', 'font_5_n', 'font_7_b', 'font_6_t', 'font_6_k', 'font_4_t', 'font_1_q', 'font_1_g', 'font_3_r', 'font_9_p', 'font_9_d', 'font_4_k', 'font_8_k', 'font_3_d', 'font_0_b', 'font_6_f', 'font_8_j', 'font_4_K'],
            ['font_3_J', 'font_1_R', 'font_2_L', 'font_2_J', 'font_7_S', 'font_3_Q', 'font_7_H', 'font_1_E', 'font_0_L', 'font_5_F', 'font_6_T', 'font_8_R', 'font_9_H', 'font_9_N', 'font_5_Q', 'font_0_T', 'font_0_c'],
            ['font_4_o', 'font_1_h', 'font_3_d', 'font_9_q', 'font_7_s', 'font_1_k', 'font_6_f', 'font_5_k', 'font_1_t', 'font_8_h', 'font_7_c', 'font_3_n', 'font_6_r', 'font_8_k', 'font_4_f', 'font_0_c', 'font_9_h', 'font_0_t', 'font_5_c'],
            ['font_9_N', 'font_8_B', 'font_2_K', 'font_3_I', 'font_5_K', 'font_3_P', 'font_4_Q', 'font_5_E', 'font_9_F', 'font_6_G', 'font_2_F', 'font_8_K', 'font_7_T', 'font_7_H', 'font_6_P', 'font_1_D', 'font_8_k']]
NOTES = [   [(45, 80, 2), (80, 80, 5)],
            [(45, 80, 2), (80, 80, 5)],
            [(45, 80, 2), (80, 80, 5)],
            [(40, 80, 4), (60, 80, 3)],
            [(40, 80, 4), (60, 80, 3)],
            [(40, 80, 4), (60, 80, 3)],
            [(40, 80, 4), (60, 80, 3)] ]


class YOLO:

    def __init__(self):
        self.mt = MyTools()
                
        self.loop = 1

        configPath = "./data/yolov3.cfg"
        weightPath = "./data/backup/yolov3_best.weights"
        metaPath   = "./data/obj.data"
            
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

        # Paramètres de detections
        print(CONF['darknet'])
        self.thresh = int(CONF['darknet']['thresh'])
        self.hier_thresh = int(CONF['darknet']['hier_thresh'])
        self.nms = int(CONF['darknet']['nms'])
        print("pb conf", self.thresh, self.hier_thresh, self.nms)
    
        # Trackbars
        self.create_trackbar()
        self.set_init_tackbar_position()

        # Create an image we reuse for each detect
        self.darknet_image = darknet.make_image(darknet.network_width(self.netMain),
                                                darknet.network_height(self.netMain),
                                                3)
        self.msg = ""

        # Midi
        fonts = CONF['midi']['fonts']
        self.player = {}
        for i in range(10):
            channel = i
            bank = 0
            bank_number = 1  # randint(0, 127)
            self.player[i] = OneInstrumentPlayer(fonts, channel, bank, bank_number)

    def play_notes(self, notes):
        """[(note, volume, police), ...] = [(45, 124, 2), ... ]"""

        print("Notes dans l'image:", notes)

        notes_en_cours = []
        for note in notes:
            notes_en_cours.append([note[0], note[2]])
        # Stop des notes en cours et absentes de notes
        for i in range(10):
            for key, val in self.player[i].thread_dict.items():
                if (key, i) not in notes_en_cours:
                    self.player[i].thread_dict[key] = 0
                    
        # play des nouvelles notes
        for note in notes:
            if 0 < note[0] < 127:
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

    def detect(self):
        fl = self.mt.get_all_files_list(SHOT_JPG, ".jpg")
        i = 0
        while self.loop:
            name = fl[i]
            i += 1
            
            # Capture des positions des sliders
            self.thresh = cv2.getTrackbarPos('threshold','Reglage')
            self.hier_thresh = cv2.getTrackbarPos('hier_thresh','Reglage')
            self.nms = cv2.getTrackbarPos('nms','Reglage')
            
            img = cv2.imread(name)
            print(name, "img.shape", img.shape)
            #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            img_resized = cv2.resize(img, (darknet.network_width(self.netMain),
                                           darknet.network_height(self.netMain)),
                                           interpolation=cv2.INTER_LINEAR)

            darknet.copy_image_from_bytes(self.darknet_image, img_resized.tobytes())
            
            # detect_image(net, meta, im, thresh=0.5, hier_thresh=0.5, nms=0.45, debug=False)
            detections_l = darknet.detect_image(self.netMain, 
                                                self.metaMain, 
                                                self.darknet_image,
                                                self.thresh/100,
                                                self.hier_thresh/100,
                                                self.nms/100)

            # Application des détections dan sl'image
            image, letters = cvDrawBoxes(detections_l, img_resized)

            # Conversion des letrres en notes
            # notes = [(note, volume, police), ...] = [(45,124, 2), ... ]
            # police = instrument
            # #if i % 2 == 0:
                # #letters = LETTERS[i]
            # #else:
                # #letters = []
                
            notes = letters_to_notes(letters)
            # #if i % 2 == 0:
                # #notes = NOTES[i]
            # #else:
                # #notes = []
            self.play_notes(notes)
            
            image = cv2.resize(image, (800, 800), interpolation=cv2.INTER_LINEAR)
            # Affichage du Semaphore
            cv2.imshow('Letters', image)
            # Affichage des trackbars
            cv2.imshow('Reglage', self.reglage_img)

            # Attente
            k = cv2.waitKey(1)
            if i == fl :
                self.loop = 0
            # Echap pour quitter
            if k == 27:
                self.loop = 0


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
    # Parcours des 10 polices possibles
    notes_d = {}
    for i in range(10):
        notes_d[i] = [0, 0]
        for letter in letters:
            police = int(letter[5])
            if police == i:
                l = letter[7]
                x = CONVERSION[l]
                #print(l, x)
                if l.islower():
                    notes_d[i][0] += x
                else:
                    print("Ajout à volume de:", x)
                    notes_d[i][1] += x
                    
    for k, v in notes_d.items():
        if v[0] != 0:
            notes.append([v[0], v[1], k])
        
    return notes


def put_text(img, text, xy, size, thickness):
    """
    Adding Text to Images:
        Text data that you want to write
        Position coordinates of where you want put it (i.e. bottom-left corner
        where data starts).
        Font type (Check cv.putText() docs for supported fonts)
        Font Scale (specifies the size of font)
        regular things like color, thickness, lineType etc. For better look,
        lineType = cv.LINE_AA is recommended.

    We will write OpenCV on our image in white color.
    font = cv.FONT_HERSHEY_SIMPLEX
    cv.putText(img, 'OpenCV', (10, 500), font, 4, (255,255,255), 2, cv.LINE_AA)
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
    """
    Cobnstruit le rectangle autour d'une détection
    """
    
    letters = []
    for detection in detections:
        # La lettre détectée
        lettre = detection[0].decode()
        # Ajout à la liste des letrres
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
        cv2.putText(img,
                    lettre +
                    " [" + str(round(detection[1] * 100, 2)) + "]",
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.1,
                    [0, 255, 0], 2)
                    
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
