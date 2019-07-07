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
Crée des images png de chaque lettre d'une liste de lettre

Entrée:
    Un dossier avec les ttf, ttfs
Sortie:
    Un dossier pngs avec
        un dossier font_1 etc 
        les png dedans

convert -background none -fill black -font font.ttf -pointsize 300
-write filename label:"Z" z.png

"""


import os, sys
import subprocess

from pymultilame import MyTools

L = "abcdefghijklmnopqrstuvwxyz"
# ["a", "b", ....]
LETTRES = list(L)

C = "0123456789"
CHIFFRES = list(C)


class TtftoPng:

    def __init__(self, size):
        self.size = size
        self.tools = MyTools()

        # 10 polices possible seulement
        # https://www.imagemagick.org/script/color.php
        self.colors = [ "SaddleBrown", "GreenYellow", "gray60", "MediumBlue",
                        "magenta2", "SpringGreen", "pink", "cyan3", "tomato",
                        "orchid3", "DimGray", "salmon","NavajoWhite4",
                        "goldenrod1", "SpringGreen", "DeepSkyBlue3",
                        "red", "blue"]
        self.color_num = 0
        
        # Create pngs directory
        self.tools.create_directory("./pngs")
        
        # Dict des dossiers avec ttf
        self.ttf_list = self.get_ttfs()
        
        # Création des sous dossiers dans ./pngs 
        self.create_sub_directories()

    def convert_ttfs(self):
        """Convertit tous les ttfs"""
        
        for rep in self.ttf_list:
            # récup du ttf
            ttf = self.tools.get_all_files_list(rep, 'ttf')
            self.convert_ttf(rep, ttf)
            self.color_num += 1
            
    def convert_ttf(self, rep, ttf):
        """Convertit un ttf"""
        
        for l in LETTRES:
            l = l.upper()
            self.convert_letter(l, rep, ttf)
            l = l.lower()
            self.convert_letter(l, rep, ttf)
        # #for c in CHIFFRES:
            # #self.convert_letter(c, rep, ttf)            
            
    def convert_letter(self, letter, rep, ttf):
        """Convertit une lettre
        Conversion de:  ./ttfs/southern/Southern.ttf
        lettre:  A
        dans: ./pngs/southern/
        command convert -background none -fill black -font
        ./ttfs/southern/Southern.ttf -pointsize 300 -write ./pngs/southern/
        label:"A" A.png
        """

        print("Conversion de {}".format(letter))
        
        filename = "./pngs" + rep[6:] + "/" + letter + ".png"

        if len(ttf) > 0:
            font = "./" + ttf[0]
            # remplacement espace dans le nom,
            # mais dossier ne doit pas avoir d'espace
            font = font.replace(' ', '\\ ')
            color = self.colors[self.color_num]
            
            print(  "Conversion de: ", font,
                    " lettre: ", letter,
                    " dans: ", filename,
                    "color", color)

            command = 'convert -background none -fill {4} -font {3} \
                       -pointsize {1} label:"{0}" {2}'.format(  letter,
                                                                self.size,
                                                                filename,
                                                                font,
                                                                color)
            print("command", command)
            
            subprocess.call(command, shell=True)
        
    def create_sub_directories(self):
        """"Création des sous dossiers dans ./pngs"""
        
        for d in self.ttf_list:
            parts = d.split("/")
            self.tools.create_directory("./pngs/" + parts[-1])
            
    def get_ttfs(self):
        # Tous les fichiers ttf
        ttfs = self.tools.get_all_sub_directories("./ttfs")

        ttf_list  = []
        
        for subdir in ttfs:
            if subdir != "./ttfs":
                dd = self.tools.get_all_sub_directories(subdir)
                for d in dd:
                    if "MACOSX" not in d:
                        if subdir not in ttf_list:
                            ttf_list.append(subdir)
        return ttf_list
        
    
if __name__ == "__main__":
    size = 300
    ttp = TtftoPng(size)
    # Conversion
    ttp.convert_ttfs()
