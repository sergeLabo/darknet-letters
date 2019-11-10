#!python3
# -*- coding: UTF-8 -*-

import os, sys
import json

# Import du dossier parent soit letters
sys.path.append("..")
from letters_path import LettersPath

lp = LettersPath()
letters_dir = lp.letters_dir
CONF = lp.conf


from pymultilame import MyTools


class IaAnalyse:

    def __init__(self):

        self.mt = MyTools()
        
        # Dossier des musiques sources "../midi/json_fps_35/non_git/pour_ia"
        self.src = CONF["play_letters"]["json_files"]
        self.src_json = self.mt.get_all_files_list(self.src, ".json")
        
        # Dossier des résultats de l'IA
        self.dossier = CONF["play_letters"]["dossier"]
        # Tous les résultats
        self.results = self.mt.get_all_files_list(self.dossier, ".json")

    def analyse(self):
        """
        src = /bla...bla/midi/json_fps_35/non_git/pour_ia/sheriff.json
        result = /bla...bla/BACKUP/play_letters_shot_jpg_3/sheriff.json
        """
        
        # Une musique source
        for src in self.src_json:
            if "bob_marley-no_woman_no_cry" in src:
                name = src.replace(self.src, "")
                result = self.dossier + name

                # Lecture des fichiers
                with open(src) as f:
                    src_data = json.load(f)
                f.close()

                with open(result) as f:
                    result = json.load(f)
                f.close()
                
                partitions = src_data["partitions"]
                instruments = src_data["instruments"]

                # 0 à 10 partitions
                # 1000 frames
                for frame in range(1, 300, 1):
                    print(frame)
                    for p in range(len(partitions)):
                        if partitions[p][frame]:
                            print("partitions", p, partitions[p][frame][0][0])
                    if result[frame]:
                        for i in range(len(result[frame])):
                            print("result", result[frame][i][0], result[frame][i][1])
            
                print("instruments", len(instruments), instruments)
            

if __name__ == "__main__":

    iaa = IaAnalyse()
    iaa.analyse()
