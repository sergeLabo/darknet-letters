#!python3
# -*- coding: UTF-8 -*-

"""
Calcul l'efficacité de l'IA
TODO expliquer les étapes

Si ESSAI = 4, play_letters analyse les images pour jouer les notes
qui sont enregistrées dans zorro_4.json dans le dossier du dossier zorro

Cette sortie est comparée avec le json d'origine qui a servi à créer les images
à décoder: ../midi/json_40/non_git/ia
"""


import os, sys
from glob import glob
from pathlib import Path
from datetime import datetime

from pymultilame import MyTools

# Import du dossier parent soit letters
# Pas d'import possible direct du dossier parent
# ValueError: attempted relative import beyond top-level package
sys.path.append("..")
from letters_path import LettersPath
lp = LettersPath()


# Définir le numéro de l'essai, utilisé dans play_letters
# Se retrouve dans le nom des json
ESSAI = lp.conf["benchmark"]["essai"]

# Dossier avec les json de musique qui ont servi à fabriquer les pl_shot
DOSSIER_IN = lp.conf["benchmark"]["dossier_in"]

# Dossier des pl_shot avec les json _4.json
DOSSIER_OUT = lp.conf["benchmark"]["dossier_out"]


class Benchmark:

    def __init__(self, name, essai, test=0):
        """Le nombre de notes de l'entrée doit être supérieur à la sortie
        Correspond à moins de 2000 images dans out !
        """

        self.name = name
        self.essai = str(essai)
        self.test = test
        
        self.mt = MyTools()

        print("\nAnalyse de:    ", self.name)
                
        # Notes en sortie 
        self.notes_out = self.get_notes_out()
        
        # frames = nombre d'images
        self.frames = len(self.notes_out)
        print("Nombre de frame dans notes out:", self.frames)

        total_out = 0
        for frame in range(self.frames):
            total_out += len(self.notes_out[frame])
        print("Nombre total de notes en sortie:", total_out)
        
        # Notes en entrée
        self.notes_in = self.get_notes_in()
        
        # Table des polices
        self.notes_out_dict_table = self.get_fonts_table()
        print("Table des polices", self.notes_out_dict_table)  # [9, 4, 2]

        # Reformattage des notes en entrées comme les notes en sortie
        self.notes_in_as_note_out = self.get_notes_in_as_note_out()

        # Réallocation des polices
        self.notes_in_corrected = self.fonts_reallocation()
        
        # Nombre de notes réelles à jouer en entrée, sans les notes []
        # et jusqu'à self.frames
        self.notes_in_nbr = self.get_notes_in_nbr()
        self.count_in = 0
                
        # L'efficacité
        self.efficiency = 0
        self.score = 0
        self.bad = 0
        
        # Exécution du script
        self.bench()
                    
    def get_notes_in(self):
        """Toutes les notes de Musique in, pas seulement celles de frames"""
        
        json_in = DOSSIER_IN + self.name + ".json"
        notes_in = self.mt.get_json_file(json_in)["partitions"]

        return notes_in

    def get_notes_out(self):
        """Récupérées dans le json créé par play_letters dans le dossier
        des dossiers des images.
        """
        if not self.test:        
            out = DOSSIER_OUT + self.name + "_" + self.essai + ".json"
        else:
            out = DOSSIER_OUT + "test/" +\
                               str(self.test) +\
                               "/" +\
                               self.name +\
                               "_" +\
                               self.essai +\
                               ".json"
                  
        print("Fichier de sortie:", out)
        notes_out = self.mt.get_json_file(out)
                                          
        return notes_out

    def get_fonts_table(self):
        """Table pour réattribuer les polices attribuées à la création
        des pl_shots.
        L'attribution est forcée dans letters_once.py pour les morceaux de
        test, pour avoir toujours les mêmes pour chaque pl_shot_xx
        """
        
        instruments_txt = DOSSIER_OUT + self.name + "/" + "instruments.txt"
        instruments = self.mt.read_file(instruments_txt)
        font_table = []
        lines = instruments.splitlines()

        # La police est le 3 ème élément
        for i in range(len(lines)):
            parts = lines[i].split(" ")
            font_table.append(int(parts[2]))

        return font_table
        
    def get_notes_in_as_note_out(self):
        """ Reconstruction des notes en entrèes comme les notes en sorties
        Les notes ne sont plus attribuées à une partition
        
        Convertit au même format que out
        de
        partition = [
                     [[[12, 127]], [[45, 127]], ... ], partiton[0]
                     [[[56, 127]], [[80, 127]], ... ], partiton[1]
                    ]
        vers
                    [
                    frame 0 [ [12, 127], [56, 127] ]
                    frame 1 [ [45, 127], [80, 127] ]
                    ]
        """

        frame_nbr = len(self.notes_in[0])
        print("Nombre de notes par partition en entrèe:", frame_nbr)
        print("Nombre de partitions:", len(self.notes_in))

        notes_in_as_note_out = []
        for n in range(frame_nbr):
            note = []
            # Parcours des partitions
            for i in range(len(self.notes_in)):
                # self.notes_in[i][n] = [[52, 127]]
                if len(self.notes_in[i][n]) > 0:
                    note.append([i , self.notes_in[i][n][0][0], 127])
                else:
                    note.append([])
            notes_in_as_note_out.append(note)
        print("Nombre de frame dans notes_in_as_note_out:", len(notes_in_as_note_out))

        return notes_in_as_note_out

    def get_notes_in_nbr(self):
        """ Nombre de notes réelles à jouer en entrée.
        Attention uniquement (2000 frames = self.frames) jouées.
        Sert à calculer l'efficacité.
        """

        notes_in_nbr = 0
        # Morceau en entrée plus grand que la sortie
        if len(self.notes_in_corrected) >= self.frames:
            for frame in range(self.frames):
                for note in self.notes_in_corrected[frame]:
                    if note:
                        notes_in_nbr += 1
        else:
            print("Le morceaux est trop court")
            notes_in_nbr = 0
            
        print("Nombre de notes réelles à jouer en entrée:", notes_in_nbr)
        
        return notes_in_nbr

    def fonts_reallocation(self):
        """Après reconstruction des notes_in comme notes_out,
        réattribution des polices définie dans letters_once.py
        [[0, 41, 127], [1, 41, 127]]
        vers
        [[8, 41, 127], [1, 41, 127]]
        """
        
        notes_in_corrected = []
        for note in self.notes_in_as_note_out:
            note_attr = []
            for i in range(len(note)):
                if note[i]:
                    new = [self.notes_out_dict_table[note[i][0]], note[i][1], 127]
                    note_attr.append(new)
            notes_in_corrected.append(note_attr)
            
        return notes_in_corrected

    def notes_bench_good(self):
        """Analyse les notes en entrée et en sortie pour trouver
        le nombre de bonnes notes
        """

        all_good_notes = []
        
        # Score des notes justes
        for frame in range(self.frames):  # 2000
            for note in self.notes_in_corrected[frame]:
                if note:
                    self.count_in += 1
                if note in self.notes_out[frame]:
                    self.score += 1
                    all_good_notes.append(note)
                    
            # #print(frame, 'in ', self.notes_in_corrected[frame],
                         # #'out', self.notes_out[frame], self.score,
                         # #'self.count_in', self.count_in)
        print("Recomptage des notes en entrée:", self.count_in)
        
        if self.count_in != 0:
            self.efficiency = round((self.score / self.count_in), 3)
            print("Nombre de notes reconnues  =", self.score,
                  "soit", self.efficiency)
        else:
            print("Pas de notes en entrées")

        # Pour calcul par police
        allocation = self.notes_allocation(all_good_notes)
        print("Répartition des bonnes notes:", allocation)

        return allocation
        
    def notes_bench_bad(self):
        """Analyse les notes en entrée et en sortie pour trouver
        les fausses notes.
        """

        all_bad_notes = []
        # Score des fausses notes
        for frame in range(self.frames):  # 2000
            for note in self.notes_out[frame]:
                if note not in self.notes_in_corrected[frame]:
                    self.bad += 1
                    all_bad_notes.append(note)
                    
        # Pour calcul par police
        allocation = self.notes_allocation(all_bad_notes)
        print("Répartition des mauvaises notes:", allocation)
        
        print("\nNombre de mauvaise notes:",  self.bad)

        return allocation
                
    def notes_allocation(self, all_notes):
        """de
        [
        [4, 45, 127], [8, 45, 127], [2, 45, 127], ...
        ]
        répartition par font
        {
        0: 20, 1: 64 ....
        }
        """
        
        # Dict du résultat
        allocation = {}
        for i in range(10):
            allocation[i] = 0

        for note in all_notes:
            allocation[note[0]] += 1

        return allocation
            
    def fonts_bench(self, allocation_good, allocation_bad):
        print("\nRapport mauvaises/bonnes:")
        for i in range(10):
            a = 0
            if allocation_good[i] != 0:
                a = allocation_bad[i] / allocation_good[i]
            print("Police:", i, "ratio", a)
            
    def bench(self):
        """Compare l'entrées et la sortie"""
        
        allocation_good = self.notes_bench_good()
        allocation_bad = self.notes_bench_bad()
        self.fonts_bench(allocation_good, allocation_bad)

            
class BenchmarkBatch:

    def __init__(self, dossier_in, dossier_out, essai, test=0):

        self.dossier_in = dossier_in
        self.dossier_out = dossier_out
        self.essai = essai
        self.test = test
        
        self.mt = MyTools()
        
        # Liste de tous les sous-dossiers
        self.get_all_sub_directories()
        
    def get_all_sub_directories(self):
        if not self.test:
            self.all_sub_directories = glob(self.dossier_out + "*/")
        else:
            out = self.dossier_out[:-5]
            self.all_sub_directories = glob(out + "*/")
            
        # Suppression du dossier 'test' de la liste
        i = 0
        for name in self.all_sub_directories:
            if "test" in name:
                break
            i += 1
        self.all_sub_directories.pop(i)
        
        # Pour affichage
        n = 0
        print("\nListe des sous dossiers des résultats d'analyse:")
        for sb in self.all_sub_directories:
            name = Path(sb).name
            print("    ", n, "name:", name, "    Répertoire:", sb)
            n += 1
        print()

    def save_efficiency(self, data):
        """Enregistrement dans le dossier out avec les autres json"""
        
        # Info générale
        data = "\n\nDossier in: {}\nDossier out: {}\nEssai: {}\n{}".format(\
                                                            self.dossier_in,
                                                            self.dossier_out,
                                                            self.essai,
                                                            data)
                                                            
        date = '{0:%Y_%m_%d-%H_%M_%S}'.format(datetime.now())
        if not self.test:
            fichier = DOSSIER_OUT + "zz_efficiency_" + date + ".txt"
        else:
            fichier = DOSSIER_OUT + str(self.test) + "_" + date + ".txt"
        print("Sauvegarde dans:")
        print("    ", fichier)
        self.mt.write_data_in_file(data, fichier, "w")
        
    def check(self, efficiency):
        i = 0
        o = 0
        for eff in efficiency:
            i += eff[1]
            o += eff[0]
        final_check = round(o / i, 3)
        print("\nEfficacité globale:", final_check)
        
        return final_check

    def batch(self):
        data = ""
        efficiency = []
        
        for sb in self.all_sub_directories:
            name = Path(sb).name
            bm = Benchmark(name, self.essai, self.test)
            data += "    Reconnue: " + str(bm.score) +\
                    "    Bad: " + str(bm.bad) +\
                    "    Name: " + name +\
                    "    Nombre de notes en entrées: " + str(bm.count_in) +\
                    "    Efficacité: " + str(bm.efficiency) + "\n"

            efficiency.append([bm.score, bm.count_in])
            
        # Vérification
        final_check = self.check(efficiency)

        data += "\nCheck final:" + str(final_check) + "\n"
                 
        print("\n\n")
        print(data)

        # Enregistrement dans un fichier
        self.save_efficiency(data)


def one_bench():
    bmb = BenchmarkBatch(DOSSIER_IN, DOSSIER_OUT, ESSAI)
    bmb.batch()


def test():
    """Pour bench fonction du temps d'apprentissage"""

    for i in range (1, 4, 1):
        indice = i * 1000
        print("\n\n\n\n\n\n\n\n")
        print("INDICE:    ", indice)
        out = DOSSIER_OUT + str(indice) + "/"
        print("DOSSIER_OUT", out)
        bmb = BenchmarkBatch(DOSSIER_IN, out, ESSAI, test=indice)
        bmb.batch()
    
if __name__ == "__main__":
    
    # #one_bench()
    test()
