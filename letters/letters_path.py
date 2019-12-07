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
Permet de récupérer la config et les chemins quelque soit le dossier d'où
est lancé un script !
"""

from pathlib import Path

from pymultilame import PathTools, MyConfig


class LettersConfig(MyConfig):

    def __init__(self, letters_dir):
        """letters_dir est un Path"""

        config_file = letters_dir / 'letters.ini'
        super().__init__(config_file, verbose=0)
        #print("Configuration chargée !\n")  # , self.conf)


class LettersPath(LettersConfig):

    def __init__(self):

        # Dossier letters
        self.get_letters_dir()

        # Chargement de la config
        super().__init__(self.letters_dir)

        # Dossiers défini dans letters.ini
        self.set_shot_dir()
        self.set_shot_jpg_dir()

        # Dossier immuable
        self.set_shot_control_dir()

        #print("Chemin absolu du dossier letters:", self.letters_dir)

    def get_letters_dir(self):

        cur_dir = Path('./').absolute()
        # Position de 'letters' dans le chemin
        d = cur_dir.parts.index('letters')
        # Coupe à la fin de tout après 'letters'
        f = len(cur_dir.parts) - d
        e = cur_dir.parts[:-f]

        # Création du Path jusque 'letters'
        self.letters_dir = Path(*e) / 'letters'

    def set_shot_control_dir(self):
        self.shot_control_dir = self.letters_dir / 'control' / 'shot_control'

    def set_shot_dir(self):
        """Chemin en str dans ini"""

        self.shot_dir = Path(self.conf["letters_shot"]["shot"])

    def set_shot_jpg_dir(self):
        """Chemin en str dans ini"""

        # #self.shot_jpg_dir = Path(self.conf["letters_shot"]["shot_jpg"])

        self.shot_jpg_dir = Path(str(self.shot_dir) + "_jpg")


    @property
    def get_letters_path(self):
        return self.letters_dir

    def get_midi_directory(self):
        return str(self.letters_dir / 'midi')


if __name__ == "__main__":
    lp = LettersPath()
    print("\nChemin du dossier midi:", lp.get_midi_directory())
    print(type(lp.get_midi_directory()))
