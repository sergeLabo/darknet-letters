#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
un canal = une police
une note =
            note de 0 à 127
            velocity = volume = 0 à 100
    note = (102, 89)
    note = (minuscule, majuscule)
    
abcdefghij = 10 lettres
0123456789

klmnopqrs = 9 lettres
123456789*10

t = 1 lettres
100

total de 20 lettres possibles

exemple:
lettres tlcDP de la police font_1
font_1 = police_1 = canal_1
note = t l c = 100 + 10 + 2 = 112
vol  = D P   = 3 + 60 = 63
"""

m = "abcdefghijklmnopqrstuvwxyz"
M = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MINUS = list(m)
MAJUS = list(M)
