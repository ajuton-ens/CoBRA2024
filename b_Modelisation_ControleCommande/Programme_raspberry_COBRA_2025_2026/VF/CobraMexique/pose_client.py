# module à importer dans le programme d'asservissement
# expose la même API que l'ancien code Localisation :
#   loc = Localisation(...)
#   loc.mesure()              -> (x, y, yaw)        ou None
#   loc.mesureSansTelemetre() -> (x, y, z, yaw)     ou None

import json
import math

FICHIER_POSE = "/tmp/pose.json"


class Localisation:
    def __init__(self, ListePoints=None):
        # ListePoints est gardé pour compatibilité avec l'ancien code
        # mais n'est pas utilisé ici (la fusion est déjà faite dans main.py)
        self.Liste_points_3D = ListePoints

    def _lire_pose(self):
        # lit le fichier de pose partagé, renvoie un dict ou None
        try:
            with open(FICHIER_POSE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def mesure(self):
        # renvoie (x, y, yaw_deg) - z est donné par le télémètre côté asservissement
        # yaw converti en degrés pour cohérence avec l'ancienne API
        pose = self._lire_pose()
        if pose is None:
            return None
        yaw_deg = math.degrees(pose["yaw"])
        return (pose["x"], pose["y"], yaw_deg)

    def mesureSansTelemetre(self):
        # renvoie (x, y, z, yaw_deg) - version complète
        pose = self._lire_pose()
        if pose is None:
            return None
        yaw_deg = math.degrees(pose["yaw"])
        return (pose["x"], pose["y"], pose["z"], yaw_deg)
