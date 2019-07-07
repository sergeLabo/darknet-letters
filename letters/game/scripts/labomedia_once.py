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
Ne jamais modifier ce script.

Les scripts:
- labomedia_once.py
- labomedia_always.py
sont les seuls scripts importés directement dans Blender.

Les autres scripts sont importés en temps que modules.

Il est alors possible de les modifier dans un éditeur externe
sans avoir à les recharger dans Blender.
'''

# imports locaux
from scripts import letters_once


def main():
    '''Fonction lancée à chaque frame dans blender en temps que module.'''

    letters_once.main()
