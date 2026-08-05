# -*- coding:utf-8 -*-
'''
  @file bmm350_compass.py
  @brief Classe d'extension pour le capteur DFRobot BMM350 permettant un calcul d'angle calibré.
'''
import math
import time
from DFRobot_bmm350 import *

class BMM350Compass:
    def __init__(self, bus):
        """
        Initialise la boussole BMM350 avec calibration.
        """
        self.bmm350 = DFRobot_bmm350_I2C(bus)
        
        # Valeurs de calibration par défaut (basées sur vos mesures)
        self.x_min, self.x_max = -20.0, 20.0
        self.y_min, self.y_max = 10.0, 40.0
        
        # Calcul initial des décalages (offsets)
        self._update_offsets()

    def _update_offsets(self):
        """Calcule en interne les offsets à partir des valeurs min/max."""
        self.x_offset = (self.x_max + self.x_min) / 2.0
        self.y_offset = (self.y_max + self.y_min) / 2.0

    def set_calibration_limits(self, x_min, x_max, y_min, y_max):
        """
        Permet d'ajuster dynamiquement les limites de calibration si nécessaire.
        """
        self.x_min, self.x_max = float(x_min), float(x_max)
        self.y_min, self.y_max = float(y_min), float(y_max)
        self._update_offsets()

    def begin(self):
        """
        Initialise et configure le capteur. 
        Renvoie True si l'initialisation réussit, False sinon.
        """
        if self.bmm350.sensor_init() == BMM350_CHIP_ID_ERROR:
            return False
            
        self.bmm350.set_operation_mode(BMM350_NORMAL_MODE)
        self.bmm350.set_preset_mode(BMM350_PRESETMODE_HIGHACCURACY, BMM350_DATA_RATE_25HZ)
        self.bmm350.set_measurement_XYZ()
        return True

    def get_heading(self):
        """
        Lit les données brutes, applique la calibration et renvoie l'angle (cap)
        compris entre 0.0 et 360.0 degrés par rapport au Nord.
        """
        geomagnetic = self.bmm350.get_geomagnetic_data()
        raw_x = geomagnetic[0]
        raw_y = geomagnetic[1]
        
        # Application de la calibration
        calibrated_x = raw_x - self.x_offset
        calibrated_y = raw_y - self.y_offset
        
        # Calcul de l'angle en radians
        compass = math.atan2(calibrated_x, calibrated_y)
        
        # Conversion en degrés
        degree = compass * 180.0 / math.pi
        
        # Normalisation entre 0 et 360°
        if degree < 0:
            degree += 360.0
            
        return round(degree, 2)

    def get_raw_and_calibrated_data(self):
        """
        Fonction utilitaire optionnelle pour voir les valeurs brutes et calibrées.
        """
        geomagnetic = self.bmm350.get_geomagnetic_data()
        raw_x, raw_y, raw_z = geomagnetic[0], geomagnetic[1], geomagnetic[2]
        return {
            "raw": (raw_x, raw_y, raw_z),
            "calibrated": (raw_x - self.x_offset, raw_y - self.y_offset, raw_z)
        }

# Exemple d'utilisation si le fichier est exécuté directement
if __name__ == "__main__":
    print("Initialisation de la boussole...")
    compass = BMM350Compass()
    
    if not compass.begin():
        print("Erreur d'initialisation du capteur BMM350. Vérifiez les branchements.")
        exit(1)
        
    print("Capteur initialisé avec succès. Rotation requise pour tester.")
    print("-" * 50)
    
    try:
        while True:
            angle = compass.get_heading()
            data = compass.get_raw_and_calibrated_data()
            print(f"Données brutes Y: {data['raw'][1]} uT | Calibrées Y: {data['calibrated'][1]:.1f} uT")
            print(f"Angle par rapport au Nord : {angle} °")
            print("-" * 50)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nArrêt du programme.")
