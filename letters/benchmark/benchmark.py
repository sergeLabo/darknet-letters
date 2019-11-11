#!python3
# -*- coding: UTF-8 -*-


import os
from time import sleep
from pymultilame import MyTools

mt = MyTools()

def concatenate_notes_in(partitions_in):
    """ de
    [[[[12, 127]], [[45, 127]]], [[[12, 127]], [[80, 127]]]]
    vers
    [
    frame 0 [[12, 127], [45, 127], [[]]],
    frame 1 [[12, 127], [80, 127]]
    ]
    """

    frame_nbr = len(partitions_in[0])
    print("Nombre de notes par partition en entrèe:", frame_nbr)
    parts_nbr = len(partitions_in)
    print("Nombre de partitions:", len(partitions_in))

    # Reconstruction des notes en entrèes comme les notes en sorties
    # Les notes ne sont plus attribuées à une partition
    notes_in = []
    for n in range(frame_nbr):
        note = []
        for i in range(parts_nbr):
            # partitions_in[i][n] = [[52, 127]]
            if len(partitions_in[i][n]) > 0:
                note.append([i , partitions_in[i][n][0][0], 127])
        notes_in.append(note)
    print("Nombre de frame dans notes_in:", len(notes_in))

    # Nombre de notes réelles à jouer en entrée
    notes_nbr = 0
    for frame in range(len(notes_in)):
        notes_nbr += len(notes_in[frame])
    print("Nombre de notes dans notes_in:", notes_nbr)
    
    return notes_in, notes_nbr

def bench(name):
    print("\n\nMusique:", name)

    # Musique in
    dossier_in = "/media/data/3D/projets/darknet-letters/letters/midi/json_40/non_git/ia/"
    partitions_in = mt.get_json_file(dossier_in + name + ".json")["partitions"]
    notes_in, notes_nbr = concatenate_notes_in(partitions_in)
            
    # Musique out
    dossier_out = "/media/serge/BACKUP/play_letters_shot/pl_shot_08_jpg/"
    notes_out = mt.get_json_file(dossier_out + name + ".json")
    print("Nombre de notes out:", len(notes_out))

    # ## Nombre de notes réelles à jouer en entrée
    # #notes_nbr = 0
    # #for frame in range(len(notes_out)):
        # #notes_nbr += len(notes_in[frame])
        
    # récup des polices
    instruments_txt = dossier_out + name + "/" + "instruments.txt"
    instruments = mt.read_file(instruments_txt)
    font_table = []
    lines = instruments.splitlines()

    for i in range(len(lines)):
        parts = lines[i].split(" ")
        font_table.append(int(parts[2]))

    print("font_table", font_table)  # [9, 4, 2]

    # Réattribution des polices
    # [[2, 41, 127], [3, 41, 127]] vers
    # [[8, 41, 127], [1, 41, 127]]
    notes_in_attr = []
    for note in notes_in:
        note_attr = []
        for i in range(len(note)):
            new = [font_table[note[i][0]], note[i][1], 127]
            note_attr.append(new)
        #print(note, note_attr)
        notes_in_attr.append(note_attr)
    
    # Score des notes justes
    score = 0
    for frame in range(1500):  # 1500 = len(notes_out)
        #print(notes_in[frame], notes_out[frame])
        # [[2, 41, 127], [3, 41, 127]] [[0, 50, 127], [4, 8, 127]]
        for note in notes_in_attr[frame]:
            #print(notes_in_attr[frame], notes_out[frame])
            if note in notes_out[frame]:
                score += 1

    if notes_nbr != 0:
        note_sur_1 = (score / notes_nbr)
    print("Nombre de notes en entrée  =", notes_nbr)
    print("Nombre de notes reconnues  =", score, "soit", round(note_sur_1, 3))


if __name__ == "__main__":
    l = [   "oh les filles oh les filles",
            "zorro",
            "Polnareff Michel - On Ira Tous Au Paradis",
            "jeux_interdits",
            "gaynor_i_will_survive",
            "Dutronc_cactus"]
    # #l = ["zorro"]
    for name in l:
        bench(name)
