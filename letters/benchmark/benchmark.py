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



from glob import glob
from pathlib import Path
from datetime import datetime

from pymultilame import MyTools


# Définir le numéro de l'essai, utilisé dans play_letters
# Se retrouve dans le nom des json
ESSAI = 4

# Dossier avec les json de musique qui ont servi à fabriquer les pl_shot
DOSSIER_IN = "../midi/json_40/non_git/ia/"

# Dossier des pl_shot avec les json _4.json
DOSSIER_OUT = "/media/serge/BACKUP/play_letters_shot/pl_shot_08_jpg_640/"


class Benchmark:

    def __init__(self, name, essai):
        """Le nombre de notes de l'entrée doit être supérieur à la sortie
        Correspond à moins de 2000 images dans out !
        """

        self.name = name
        self.essai = str(essai)
        self.mt = MyTools()

        print("\nAnalyse de:    ", self.name)
                
        # Notes en sortie 
        self.notes_out = self.get_notes_out()
        
        # frames = nombre d'images
        self.frames = len(self.notes_out)
        print("Nombre de frame dans notes out:", self.frames)

        # Notes en entrée
        self.notes_in = self.get_notes_in()
        
        # Table des polices
        self.fonts_table = self.get_fonts_table()
        print("Table des polices", self.fonts_table)  # [9, 4, 2]

        # Reformattage des notes en entrées comme les notes en sortie
        self.notes_in_as_note_out = self.get_notes_in_as_note_out()

        # Réallocation des polices
        self.notes_in_corrected = self.fonts_reallocation()
        
        # Nombre de notes réelles à jouer en entrée, sans les notes []
        # et jusqu'à self.frames
        self.notes_in_nbr = self.get_notes_in_nbr()
        
        # L'efficacité
        self.efficiency = 0
        self.score = 0
        
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
        
        notes_out = self.mt.get_json_file(DOSSIER_OUT + self.name + "_" +\
                                          self.essai + ".json")
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
        Attention uniquement 2000 frames jouées.
        Sert à calculer l'efficacité.
        """

        notes_in_nbr = 0
        # Morceau en entrée plus grand que la sortie
        if len(self.notes_in_corrected) >= self.frames:
            for frame in range(self.frames):
                if len(self.notes_in_corrected[frame]) > 0:
                    notes_in_nbr += len(self.notes_in_corrected[frame][0])
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
                    new = [self.fonts_table[note[i][0]], note[i][1], 127]
                else:
                    new = []
                note_attr.append(new)
            notes_in_corrected.append(note_attr)
            
        return notes_in_corrected
            
    def bench(self):
        """Compare l'entrées et la sortie"""
        
        # Score des notes justes
        for frame in range(self.frames):  # 2000
            #print(frame, notes_in_corrected[frame])
            for note in self.notes_in_corrected[frame]:
                if note in self.notes_out[frame]:
                    self.score += 1

        if self.notes_in_nbr != 0:
            self.efficiency = round((self.score / self.notes_in_nbr), 3)
            print("Nombre de notes reconnues  =", self.score,
                  "soit", self.efficiency)
        else:
            print("Pas de notes en entrées")
            

class BenchmarkBatch:

    def __init__(self, dossier_in, dossier_out, essai):

        self.dossier_in = dossier_in
        self.dossier_out = dossier_out
        self.essai = essai
        self.mt = MyTools()
        
        # Liste de tous les sous-dossiers
        self.get_all_sub_directories()
        
    def get_all_sub_directories(self):
        self.all_sub_directories = glob(self.dossier_out + "*/")

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
        print(data)
        date = '{0:%Y_%m_%d-%H_%M_%S}'.format(datetime.now())
        fichier = DOSSIER_OUT + "zz_efficiency_" + date + ".txt"
        
        print("Sauvegarde dans:")
        print("    ", fichier)
        self.mt.write_data_in_file(data, fichier, "w")
        
    def batch(self):
        data = ""
        for sb in self.all_sub_directories:
            name = Path(sb).name
            #if name == "zorro":
            bm = Benchmark(name, self.essai)
            data += "    Reconnue: " + str(bm.score) +\
                    "    Name: " + name +\
                    "    Nombre de notes en entrées: " + str(bm.notes_in_nbr) +\
                    "    Efficacité: " + str(bm.efficiency) + "\n"
        print("\n\n")
        print(data)

        # Enregistrement dans un fichier
        self.save_efficiency(data)
        

if __name__ == "__main__":
    
    bmb = BenchmarkBatch(DOSSIER_IN, DOSSIER_OUT, ESSAI)
    bmb.batch()
