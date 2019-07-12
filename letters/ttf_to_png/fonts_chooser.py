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


import os, sys
import subprocess
import cv2

from pymultilame import MyTools


class FontsChooser:
    """
    /media/data/3D/projets/darknet-letters/letters/ttf_to_png/pngs/CognacRum/Z.png
    """
    
    def __init__(self):
        self.tools = MyTools()

        # Liste des images du répertoire
        root = "/media/data/3D/projets/darknet-letters/letters/ttf_to_png"
        imgs = self.tools.get_all_files_list(root + "/pngs", ".png")
        
        # [... , CognacRum ,Z.png]
        
        for img in imgs:
            if "a.png" in img or "A.png" in img:
                name_list = img.split("/")
                name = name_list[-2] + "_" + name_list[-1]
                file_name = root + "/fonts_chooser/" + name
                print(file_name)

                image = cv2.imread(img, cv2.IMREAD_UNCHANGED)
                cv2.imwrite(file_name, image)

        
    
if __name__ == "__main__":
    fc = FontsChooser()
