#!python3
# -*- coding: UTF-8 -*-


"""
Reconnaissance de lettres dans une image

La lib
        libdarknet.so
doit être dans le dossier darknet de darknet-letters,
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

from pymultilame import MyConfig


class YOLO:
    """Reset du message avec espace"""

    def __init__(self, cam, calcul, config):

        # L'objet config de darknet.ini
        self.config = config
        
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
        self.thresh = self.config.conf['darknet']['thresh']
        self.hier_thresh = self.config.conf['darknet']['hier_thresh']
        self.nms = self.config.conf['darknet']['nms']

        # Trackbars
        self.create_trackbar()
        self.set_init_tackbar_position()

        # Create an image we reuse for each detect
        self.darknet_image = darknet.make_image(darknet.network_width(self.netMain),
                                                darknet.network_height(self.netMain),
                                                3)
        self.msg = ""

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

        self.cf.save_config(section, key, value)

    def detect(self):
        while self.loop:

            # Capture des positions des sliders
            self.thresh = cv2.getTrackbarPos('threshold','Reglage')
            self.hier_thresh = cv2.getTrackbarPos('hier_thresh','Reglage')
            self.nms = cv2.getTrackbarPos('nms','Reglage')

            ret, frame_read = self.cap.read()
            frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)

            # Image carrée
            frame_rgb = crop(frame_rgb)

            frame_resized = cv2.resize(frame_rgb,
                                       (darknet.network_width(self.netMain),
                                        darknet.network_height(self.netMain)),
                                        interpolation=cv2.INTER_LINEAR)

            darknet.copy_image_from_bytes(self.darknet_image, frame_resized.tobytes())
            # detect_image(net, meta, im, thresh=0.5, hier_thresh=0.5, nms=0.45, debug=False)
            detections, tag, confiance = darknet.detect_image(self.netMain,
                                                              self.metaMain,
                                                              self.darknet_image,
                                                              self.thresh/100,
                                                              self.hier_thresh/100,
                                                              self.nms/100)

            try:
                image = cvDrawBoxes(detections, frame_resized)
            except:
                image = frame_read

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (900, 900), interpolation=cv2.INTER_LINEAR)

            # Affichage du message
            put_text(image, "Message:", (20, 45), 1, 2)
            for i in range(len(msg)):
                y = int(105 + 50*i)
                put_text(image, msg[i], (20, y), 2, 3)

            put_text(image, "Espace: reset du message", (20, 870), 1, 2)

            # Affichage du Semaphore
            cv2.imshow('Semaphore', image)
            # Affichage des trackbars
            cv2.imshow('Reglage', self.reglage_img)

            # Attente
            k = cv2.waitKey(3)
            # Espace pour reset du message
            if k == 32:
                self.msg = ""
            # Echap pour quitter
            if k == 27:
                self.loop = 0

        self.cap.release()


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
    
    for detection in detections:
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
                    detection[0].decode() +
                    " [" + str(round(detection[1] * 100, 2)) + "]",
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    [0, 255, 0], 2)
    return img


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

    dossier = os.getcwd()
    config = MyConfig(dossier + "/darknet.ini")

    yolo = YOLO(config)
    yolo.detect()
