#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:29:10 2025

@author: salybey
"""

# Derniere modif: 14/03/2025

import smbus2  
import cobra_pca9685_v03

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = cobra_pca9685_v03.PCA9685(myi2cbus) # Initialisation du générateur de PWM

numeros_moteurs = {"brushless": [0, 1, 2, 3, 4], "MCC": [[5, 6], [7, 8]]}

mot = []
for i in range(0,4):
    mot.append(cobra_pca9685_v03.brushless(myPCA9685,i)) # Initialisation du moteur
print("Prêt - Initialisation réalisée")

# Boucle_continue/principale
while True : 
    numero_moteur=int(input("Donner numero moteur:"))
    commande_vitesse_pourcentage=int(input("Donner la commande de vitesse du moteur en pourcentage (entre -100 et 100):"))
    
    mot[numero_moteur].cmd_vit_pourcent(commande_vitesse_pourcentage)