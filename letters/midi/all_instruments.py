#!python3
# -*- coding: UTF-8 -*-

"""
"music/non_git/Itsi_bitsi_petit_bikini-Dalida.mid": [[[0, 113], true, "DRUM R-8            "], [[0, 3], false, "BASS S-330          "], [[0, 64], false, "FANTASY D-110       "], [[0, 79], false, "BRASS D-50          "], [[0, 61], false, "PIANO MKS-20        "], [[0, 11], false, "GUITARE PROTEUS     "], [[0, 7], false, "GUITARE PROTEUS     "], [[0, 0], false, "Mel"], [[8, 117], true, "tom10               "]],

vers


"""


from pymultilame import MyTools

mt = MyTools()

data = mt.get_json_file("./all_instruments_40.json")

lines = ""
for key, val in data.items():
    name = key.replace("music/", "")
    name = name.replace("non_git/", "")
    name = name.replace("ia/", "")

    nb = 0
    lines += name + "\n\n"
    for instrument in val:
        # [[0, 113], true, "DRUM R-8            "]
        bank = instrument[0][0]
        piste = instrument[0][1]
        drum = instrument[1]
        comment = instrument[2]
        nb += 1
        lines = lines \
                + " " + str(bank) \
                + " " + str(piste) \
                + " " + str(drum) \
                + " " + str(comment) \
                + "\n"
                
    lines = lines + "\n" + "Nombre d'instruments: " + str(nb) + "\n"
    lines += "\n\n\n\n"
    print(name)
    print("Nombre d'instruments:", nb)
    print(lines)

mt.write_data_in_file(lines, "./all_instuments.txt", "w")
