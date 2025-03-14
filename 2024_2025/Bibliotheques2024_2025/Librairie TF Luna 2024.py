#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:14:05 2025

@author: salybey
"""

# Derniere modif: 14/03/2025

import smbus2 

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C

class LidarTFLuna: # pour lire la distance mesurée par le LiDAR TF Luna en utilisant le protocole I2C
    def __init__(self, bus, i2c_address=0x10):
        self.address = i2c_address
        self.bus = bus
    
    def read_distance(self):
        # Le TF Luna envoie les données de distance en 2 octets
        try:
            # Lire les 2 bytes (octets) de données de distance
            distance_data = self.bus.read_i2c_block_data(self.address, 0x00, 2)  #arguments: adresse unique du périphérique, adresse du premier registre à lire,  nbre de bytes à lire
            # Combiner les 2 octets en une seule valeur de distance en cm
            distance = (distance_data[0] + (distance_data[1] << 8))
            return distance
        except Exception as e:
            print(f"Erreur de lecture du LiDAR TF Luna : {e}")
            return None

lidar = LidarTFLuna(myi2cbus) # Initialisation du télémètre infrarouge
print("Prêt - Initialisation réalisée")

# Boucle_continue/principale
while True : 
    distance = lidar.read_distance()  # Récupération de la distance mesurée par le télémètre infrarouge
    print(f"La distance mesurée par le télémètre infrarouge est: {distance}cm")
    if distance<2:  # Pour arrêter la boucle infinie de mesure: placer un objet à moins de 2cm du télémètre
        break