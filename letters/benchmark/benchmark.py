#!python3
# -*- coding: UTF-8 -*-


import os
from time import sleep
from pymultilame import MyTools
from in_raw import part_1

mt = MyTools()

def concatenate_notes_in(partitions_in):
    """ Convertit au même format que out
    de
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
            else:
                note.append([])
        notes_in.append(note)
    print("Nombre de frame dans notes_in:", len(notes_in))

    return notes_in


def get_real_notes_in_number(notes_in, frames):
    """ Nombre de notes réelles à jouer en entrée.
    Attention uniquement 2000 frames jouées.
    """

    #print(notes_in)
    notes_in_nbr = 0
    if len(notes_in) > frames:
        for frame in range(frames):
            if len(notes_in[frame]) > 0:
                # #print(notes_in[frame][0])
                notes_in_nbr += len(notes_in[frame][0])
    else:
        print("Le morceaux est trop court")
        notes_in_nbr = 0
        
    print("Nombre de notes réelles à jouer en entrée:", notes_in_nbr)

    return notes_in_nbr

    
def bench(name):
    print("\n\nMusique:", name)

    # Musique in
    dossier_in = "/media/data/3D/projets/darknet-letters/letters/midi/json_40/non_git/ia/"
    partitions_in = mt.get_json_file(dossier_in + name + ".json")["partitions"]
    print(len(part_1))  #partitions_in)
    notes_in = concatenate_notes_in(partitions_in)
            
    # Musique out
    dossier_out = "/media/serge/BACKUP/play_letters_shot/pl_shot_08_jpg_640/"
    notes_out = mt.get_json_file(dossier_out + name + "_4.json")
    frames = len(notes_out)
    print("Nombre de frame dans notes out:", frames)
    # #for frame in range(len(notes_out)):
        # #print(frame, notes_out[frame])

    # Nombre de notes total dans note_out
    note_out_total = 0
    for frame in range(frames):
        note_out_total += len(notes_out[frame])

    # Nombre de notes réelles à jouer en entrée, sans les notes []
    notes_in_nbr = get_real_notes_in_number(notes_in, frames)
    
    # récup des polices
    instruments_txt = dossier_out + name + "/" + "instruments.txt"
    #print("Fichier instruments_txt", instruments_txt)
    instruments = mt.read_file(instruments_txt)
    font_table = []
    lines = instruments.splitlines()
    
    for i in range(len(lines)):
        parts = lines[i].split(" ")
        font_table.append(int(parts[2]))

    #print("font_table", font_table)  # [9, 4, 2]

    # Réattribution des polices
    # [[2, 41, 127], [3, 41, 127]] vers
    # [[8, 41, 127], [1, 41, 127]]
    notes_in_attr = []
    for note in notes_in:
        note_attr = []
        for i in range(len(note)):
            if note[i]:
                new = [font_table[note[i][0]], note[i][1], 127]
            else:
                new = []
            note_attr.append(new)
        #print(note, note_attr)
        notes_in_attr.append(note_attr)
    
    # Score des notes justes
    score = 0
    for frame in range(len(notes_out)):
        #print(notes_in[frame], notes_out[frame])
        # [[2, 41, 127], [3, 41, 127]] [[0, 50, 127], [4, 8, 127]]
        for note in notes_in_attr[frame]:
            #print(frame, notes_in_attr[frame], notes_out[frame])
            if note in notes_out[frame]:
                score += 1

    if notes_in_nbr != 0:
        note_sur_1 = (score / notes_in_nbr)
        print("Nombre de notes en entrée  =", notes_in_nbr)
        print("Nombre de notes reconnues  =", score, "soit", round(note_sur_1, 3))
    else:
        print("Pas de notes en entrées")
        

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
