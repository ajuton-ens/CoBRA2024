#!/usr/bin/python
# Derniere modif: 14/03/2025

import smbus2  
import time
import cobra_TFLUNA_v03

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
mylidar = cobra_TFLUNA_v03.LidarTFLuna(myi2cbus) # Initialisation du télémètre infrarouge

# Boucle_continue/principale
while True :
    distance = mylidar.read_distance()  # Récupération de la distance mesurée par le télémètre infrarouge
    print(f"La distance mesurée par le télémètre infrarouge est: {distance}cm")
    time.sleep(0.1)