# Remplace l'ancienne FusionsCapteurs
# La fusion (LiDAR + caméras + Kalman) est maintenant faite dans main.py
# Ce fichier ne fait que lire le fichier /tmp/pose.json
# Interface identique à l'ancienne version - aucun changement dans le main asservissement

import json
from math import cos, sin, pi

FICHIER_POSE = "/tmp/pose.json"


class FusionsCapteurs:
    def __init__(self, myi2cbus):
        # myi2cbus gardé pour compatibilité - pas utilisé ici
        # car la lecture des capteurs est faite dans main.py (localisation)
        self.bus = myi2cbus

        self.x = 0
        self.y = 0
        self.z = 0
        self.lacet = 0    # en degrés

    def update(self, dt):
        # lit le fichier de pose partagé écrit par main.py
        try:
            with open(FICHIER_POSE, "r") as f:
                pose = json.load(f)
            self.x = pose["x"]
            self.y = pose["y"]
            self.z = pose["z"]
            self.lacet = pose["yaw"]    # converti en degrés
        except (FileNotFoundError, json.JSONDecodeError):
            pass    # garde les anciennes valeurs si pose pas dispo

    def Stop(self):
        # rien à arrêter ici, main.py tourne séparément
        pass

    def RepTags_to_RepCobra(self, X0, Y0):
        # changement de repère - identique à l'original
        X1 = (X0 - self.x) * cos(self.lacet * pi/180) + (Y0 - self.y) * sin(self.lacet * pi/180)
        Y1 = (Y0 - self.y) * cos(self.lacet * pi/180) - (X0 - self.x) * sin(self.lacet * pi/180)
        return (X1, Y1)

    def relative_lacet(self, lacet_consigne):
        # identique à l'original
        return (self.lacet - (lacet_consigne % 360) + 180) % 360 - 180
