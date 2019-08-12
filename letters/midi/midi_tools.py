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
Lance en terminal les différentes étapes pour:
    - jouer les midis
    - convertir les midis en json
    - jouer les json
"""


import os, sys
import subprocess
from time import sleep

from pymultilame import MyTools, MyConfig


menu_1 = """\n\n    Menu principal
        Choisir 1 pour créer les images NB 320x320
        Choisir 2 pour retailler les images
        Choisir 3 pour créer le fichier compressé des images
        Choisir 4 pour excécuter l'apprentissage de l'IA
        Choisir 5 pour tester l'IA
        Choisir 6 pour modifier la configuration
        Choisir 0 pour quitter
        """

menu_2 = """\n\nConfiguration
        Choisir 1 pour Définir blur
        Choisir 2 pour Définir learning rate
        Choisir 3 pour Définir Gris ou Noir et Blanc
        Choisir 4 pour Définir le nombre d'images pour l'apprentissage
        Choisir 5 pour Définir le nombre d'images pour tester
        Choisir 0 pour retour au menu principal
        """


def clear():
    """Efface le terminal"""

    # Windows
    if os.name == 'nt':
        os.system('cls')

    # Mac and Linux (os.name is 'posix')
    else:
        os.system('clear')


class LettersConfig(MyConfig):

    def __init__(self):
        """self.conf est le dict de la config définie dans global.ini"""

        path = MyTools().get_absolute_path(__file__)
        print("Nom de ce script:", os.path.basename(path))  # semaphore.py

        self.root = os.path.split(path)[0]
        print("Path du projet:", self.root)  #'/media/data/3D/projets/semaphore'

        ini_file = os.path.join(self.root, "global.ini")
        super().__init__(ini_file)


class LettersMenu(LettersConfig):
    """Menu de tout le projet semaphore"""

    global menu_1, menu_2

    def __init__(self):
        super().__init__()

        self.result = 0
        self.learning_rate = self.conf['ia']['learning_rate']
        self.size = self.conf['ia']['size']
        self.blur = self.conf['ia']['blur']
        self.train = self.conf['ia']['training']
        self.test = self.conf['ia']['testing']
        self.size = self.conf['ia']['size']
        self.gray = self.conf['ia']['gray']
        self.failed = self.conf['ia']['failed']

    def menu(self):
        global menu_1

        choice ='0'
        while choice == '0':
            if self.result:
                print("Result:", self.result)
            print(menu_1)

            choice = input("Votre choix: ")

            if choice == "1":  # Blender
                print("Création des images 320x320 en NB")
                blend = os.path.join(self.root,
                                    'get_training_shot',
                                    'get_training_shot.blend')

                # pb fini le script
                p = subprocess.run(["xterm",
                                    "-e",
                                    "blenderplayer",
                                    blend],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

            elif choice == "2":  # resize
                print("Resize en 40x40 et blur des images du 1")
                rb = ResizeBlur(self.root, self.size, self.blur)
                rb.batch()
                clear()
                self.menu()

            elif choice == "3":  # Compression
                print("\nCompression des images de shots")
                sc = ShotsCompression(  self.root, self.train, self.test,
                                        self.size, self.gray)
                sc.create_semaphore_npz()
                clear()
                self.menu()

            elif choice == "4":  # IA training
                print("\nApprentissage de l'IA")
                sia = SemaphoreIA(self.root, self.train, self.learning_rate)
                sia.training()
                clear()
                self.menu()

            elif choice == "5":  # IA testing
                print("\nTest de l'IA")
                sia = SemaphoreIA(self.root, self.train, self.learning_rate, self.failed)
                r = sia.testing()
                self.result = "{}".format(round(r, 2), '.2f')
                clear()
                self.menu()

            elif choice == "6":  # config
                print("Modification de la configuration")
                self.config_menu()

            elif choice == "0":
                choice = 0

            else:
                clear()
                self.menu()

        print("\n\nLe chemin est long du projet à la chose. Molière")
        os._exit(0)

    def config_menu(self):
        global menu_2

        choice ='0'
        clear()
        print(menu_2)

        while choice == '0':
            choice = input("Votre choix: ")

            if choice == "1":
                print('Blur =', self.blur)
                b = input('\n    Saisir la nouvelle valeur: ')
                b = int(b)
                if 0 <= b <= 10:
                    self.blur = b
                    self.save_config('ia', 'blur', b)
                    sleep(5)
                clear()
                self.config_menu()

            elif choice == "2":
                print('Learning Rate =', self.learning_rate)
                l = input('\n    Saisir la nouvelle valeur: ')
                l = float(l)
                if 0 < l < 1:
                    self.learning_rate = l
                    self.save_config('ia', 'learning_rate', l)
                    sleep(5)
                clear()
                self.config_menu()

            elif choice == "3":
                # Gris ou Noir et Blanc
                print("Apprentissage de l'IA avec des images en gris ou en NB")
                print('Gray actuel:', self.gray)
                print('0 = Noir et Blanc')
                print('1 = Gris')
                l = input('\n    Saisir la nouvelle valeur 0 ou 1: ')
                l = int(l)
                if  l in [0, 1]:
                    self.gray = l
                    self.save_config('ia', 'gray', l)
                    sleep(5)
                clear()
                self.config_menu()

            elif choice == "4":
                # Learning
                print("Nombre d'images d'apprentissage actuel:", self.train)
                l = input('\n    Saisir la nouvelle valeur: ')
                l = int(l)
                if  l in range(60001):
                    self.train = l
                    self.save_config('ia', 'training', l)
                    sleep(5)
                clear()
                self.config_menu()

            elif choice == "5":
                # Learning
                print("Nombre d'images de test actuel:", self.test)
                l = input('\n    Saisir la nouvelle valeur: ')
                l = int(l)
                if  l in range(60001):
                    self.test = l
                    self.save_config('ia', 'testing', l)
                    sleep(5)
                clear()
                self.config_menu()

            elif choice == "0":
                clear()
                self.menu()


if __name__ == "__main__":
    LettersMenu()
