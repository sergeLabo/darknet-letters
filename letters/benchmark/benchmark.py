#!python3
# -*- coding: UTF-8 -*-

from pymultilame import MyTools

mt = MyTools()

def flattenNestedList(nestedList):
    """Converts a nested list to a flat list."""
    
    flatList = []

    for elem_0 in nestedList:
        for elem_1 in elem_0:
            if isinstance(elem_1, list):
                if len(elem_1) > 0:
                    if len(elem_1[0]) == 2:
                        flatList.append(elem_1)

    return flatList


def bench(name):
    print("\n\nMusique:", name)

    # Musique in
    dossier_in = "/media/data/3D/projets/darknet-letters/letters/midi/json_40/non_git/ia/"
    notes_in = mt.get_json_file(dossier_in + name + ".json")["partitions"]

    # Musique out
    dossier_out = "/media/serge/BACKUP/play_letters_shot/pl_shot_08_jpg/"
    notes_out = mt.get_json_file(dossier_out + name + ".json")
    
    # récup des polices
    instruments_txt = dossier_out + name + "/" + "instruments.txt"
    instruments = mt.read_file(instruments_txt)
    font_table = []
    lines = instruments.splitlines()

    for i in range(len(lines)):
        parts = lines[i].split(" ")
        font_table.append(int(parts[2]))

    print("font_table", font_table)

    # Nombre de notes total en entrée
    flat_notes_in = flattenNestedList(notes_in)
    notes_nbr = len(flat_notes_in)

    # Score des notes justes
    score_good = 0

    print("Nombre de notes de l'IA:", len(notes_out))

    for k in range(len(notes_out)):
        targets = []
        for i in range(len(notes_in)):
            if isinstance(notes_in[i][k], list):
                if notes_in[i][k]:
                    targets.append([font_table[i],
                                    notes_in[i][k][0][0],
                                    notes_in[i][k][0][1]])
        
        for target in targets:
            if target in notes_out[k]:
                score_good += 1
        
    print("Nombre total de notes en entrée =", notes_nbr)
    print("Nombre de notes bien reconnues  =", score_good)

    note_sur_1 = (score_good / notes_nbr)
    print(round(note_sur_1, 3))


if __name__ == "__main__":
    l = [   "oh les filles oh les filles",
            "zorro",
            "Polnareff Michel - On Ira Tous Au Paradis",
            "jeux_interdits",
            "gaynor_i_will_survive",
            "Dutronc_cactus"]
    # #l = ["Dutronc_cactus"]
    for name in l:
        bench(name)
