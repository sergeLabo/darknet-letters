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

'''
Lancé à chaque frame durant tout le jeu.
'''

import random

from pymultilame import MyTools
from pymultilame import get_all_objects

from bge import logic as gl


def main():
    gl.tempo.update()
    
    all_obj = get_all_objects()
    apply_new_texture()
    print(gl.tempo["test"].tempo)

def apply_new_texture():
    if gl.tempo["test"].tempo == 0:
        n = random.randint(0, 9)
        print("n", n)
        new_tex = "//textures/pngs/font_" + str(n) + "/A.png"
        gl.tc.texture_new(new_tex)
