#!python3
# -*- coding: UTF-8 -*-

"""
Calcul l'efficacité de l'IA
TODO expliquer les étapes

Si ESSAI = 4, play_letters analyse les images pour jouer les notes
qui sont enregistrées dans zorro_4.json dans le dossier du dossier zorro

Cette sortie est comparée avec le json d'origine qui a servi à créer les images
à décoder: ../midi/json_40/non_git/ia

Définir les valeurs de la section [benchmark] dans letters.ini
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


class Benchmark:
    """Fait le bench pour une musique, un json"""
    
    def __init__(self, d_in , d_out, name, essai, test=0):
        """Le nombre de notes de l'entrée doit être supérieur à la sortie
        Correspond à moins de 2000 images dans out !
        """

        self.d_in = d_in
        self.d_out = d_out
        self.name = name
        self.essai = str(essai)
        self.test = test
        
        self.mt = MyTools()

        print("Analyse de:    ", self.name)
                
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
        self.good = 0
        self.bad = 0
        
        # Exécution du script
        self.bench()
                    
    def get_notes_in(self):
        """Toutes les notes de Musique in, pas seulement celles de frames"""
        
        json_in = self.d_in + self.name + ".json"
        notes_in = self.mt.get_json_file(json_in)["partitions"]

        return notes_in

    def get_notes_out(self):
        """Récupérées dans le json créé par play_letters dans le dossier
        des dossiers des images.
        """
        
        if not self.test:        
            out = self.d_out + self.name + "_" + self.essai + ".json"
        else:
            print("Essai", self.essai, "Test", self.test)
            # /media/data/3D/test_26/1000/Dutronc_cactus_26.json
            out = self.d_out + self.name + "_" + self.essai + ".json"

        print("Fichier de sortie:", out)
        notes_out = self.mt.get_json_file(out)
                                          
        return notes_out

    def get_fonts_table(self):
        """Table pour réattribuer les polices attribuées à la création
        des pl_shots.
        L'attribution est forcée dans letters_once.py pour les morceaux de
        test, pour avoir toujours les mêmes pour chaque pl_shot_xx

        Dans *.ini
        [benchmark]
        dossier_out = "/media/data/3D/pl_shot_99_jpg/test_27/"
        """

        if not self.test:
            instruments_txt = self.d_out + self.name + "/" + "instruments.txt"
        else:
            # Récup de /media/data/3D/pl_shot_99_jpg/
            cur_dir = Path(self.d_out)
            # Suppr des 2 derniers
            l = list(cur_dir.parts)[:-2]
            parent_dir = os.path.join(*l) + "/"
            print("parent_dir", parent_dir)
            instruments_txt = parent_dir + self.name + "/" + "instruments.txt"
            
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
        print("Nombre de frame dans notes_in_as_note_out:",
                                    len(notes_in_as_note_out))

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
        for frame in range(self.frames): # 2000 ou moins
            for note in self.notes_in_corrected[frame]:
                if note:
                    self.count_in += 1
                if note in self.notes_out[frame]:
                    self.good += 1
                    all_good_notes.append(note)
                    
            # #print(frame, 'in ', self.notes_in_corrected[frame],
                         # #'out', self.notes_out[frame], self.good,
                         # #'self.count_in', self.count_in)
        print("Recomptage des notes en entrée:", self.count_in)
        
        if self.count_in != 0:
            self.efficiency = round((self.good / self.count_in), 3)
            print("Nombre de notes reconnues  =", self.good,
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
    """Fait le bench pour un fichier de weigths, soit 6 json"""
    
    def __init__(self, d_in, d_out, essai, test=0):

        self.d_in = d_in
        self.d_out = d_out
        self.essai = essai
        self.test = test
        print("\n\n\n\nBenchmarkBatch de", d_in, d_out, essai, test)
        
        self.mt = MyTools()
        
        # Liste de tous les sous-dossiers
        self.get_all_sub_directories()
        
    def get_all_sub_directories(self):
        # Sous dossiers
        if not self.test:
            self.all_sub_directories = glob(self.d_out + "*/")
        else:
            # Récup de /media/data/3D/pl_shot_99_jpg/
            cur_dir = Path(self.d_out)
            # Suppr des 2 derniers
            l = list(cur_dir.parts)[:-2]
            parent_dir = os.path.join(*l) + "/"
            print("parent_dir", parent_dir)
            
            self.all_sub_directories = glob(parent_dir + "*/")
            
        # Suppression du dossier 'test' de la liste
        for dossier in self.all_sub_directories:
            if "test" in dossier:
                self.all_sub_directories.remove(dossier)

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
                                                            self.d_in,
                                                            self.d_out,
                                                            self.essai,
                                                            data)

        # Sauvegarde
        date = '{0:%Y_%m_%d-%H_%M_%S}'.format(datetime.now())
        if not self.test:
            fichier = self.d_out + "z_efficiency_" + date + ".txt"
        else:
            fichier = self.d_out + str(self.test) + "_" + date + ".txt"
        print("Sauvegarde dans:")
        print("    ", fichier)
        self.mt.write_data_in_file(data, fichier, "w")
        
    def check(self, efficiency):
        
        i = 0
        o = 0
        for eff in efficiency:
            i += eff[1]
            o += eff[0]
        
        return o, i

    def batch(self):
        data = ""
        good = []
        bad = []
        
        for sb in self.all_sub_directories:
            name = Path(sb).name
            bm = Benchmark(self.d_in, self.d_out, name, self.essai, self.test)
            data += "    Bonnes: " + str(bm.good) +\
                    "    Mauvaises: " + str(bm.bad) +\
                    "    Name: " + name +\
                    "    Nombre de notes en entrées: " + str(bm.count_in) +"\n"
            print(data)
            
            good.append([bm.good, bm.count_in])
            bad.append([bm.bad, bm.count_in])
            
        # Vérification
        final_good = self.check(good)
        final_bad = self.check(bad)
                 
        # Enregistrement dans un fichier
        if not self.test:
            self.save_efficiency(data)

        # Verif pour multibenchbatch
        print("% Bonne:", final_good, " - % Mauvaise:", final_bad)
        
        return final_good, final_bad

    
def benchbatch(d_in, d_out, essai, test=0):
    bmb = BenchmarkBatch(d_in, d_out, essai, test=0)
    bmb.batch()
    

def multibenchbatch(d_in, d_out, essai):
    """Pour bench fonction du temps d'apprentissage
    essai 26
    d_in "../midi/json_40/non_git/ia/"
    d_out "/media/data/3D/test_26/"
    """

    # A imprimer dans le txt à la fin, formater pour copie dans libre office
    data = ""
    
    # Liste des sous dossiers
    sd_out_list = glob(d_out + "*/")
    
    print("Liste des sous dossiers:", sd_out_list)
    
    for sd_out in sd_out_list:
        bmb = BenchmarkBatch(d_in, sd_out, essai, test=essai)
        final_good, final_bad = bmb.batch()
        w = Path(sd_out).name
        data += w + " " +\
                str(final_good[1]) + " " +\
                str(final_good[0]) + " " +\
                str(final_bad[0]) + "\n"

    print("\n\n\n\n")
    print(data)
    
                
if __name__ == "__main__":
    
    # Définir le numéro de l'essai, utilisé dans play_letters
    # Se retrouve dans le nom des json
    essai = lp.conf["benchmark"]["essai"]

    # Dossier avec les json de musique qui ont servi à fabriquer les pl_shot
    d_in = lp.conf["benchmark"]["dossier_in"]

    # Dossier des pl_shot avec les json cactus_26.json
    d_out = lp.conf["benchmark"]["dossier_out"]

    print("Essai      :", essai)
    print("Dossier in :", d_in)
    print("Dossier out:", d_out)
    
    # ## Bench d'un fichier weights
    # #benchbatch(d_in, d_out, essai, test=0)

    # Bench d'une liste de weigths
    multibenchbatch(d_in, d_out, essai)
