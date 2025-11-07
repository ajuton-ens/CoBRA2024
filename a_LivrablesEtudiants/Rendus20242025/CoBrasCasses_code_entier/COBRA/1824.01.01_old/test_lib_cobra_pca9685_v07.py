#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:29:10 2025

@author: salybey
"""

# Derniere modif: 14/03/2025

import smbus2
import cobra_pca9685_v07

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = cobra_pca9685_v07.PCA9685(myi2cbus) # Initialisation du générateur de PWM

numeros_moteurs = {"brushless": [0, 1, 2, 3, 4], "MCC": [[5, 6], [7, 8]]}

brushless = {}
servo = {}

servo["cerceau"]= cobra_pca9685_v07.servo(myPCA9685,4, "FUTABA S3107")
servo["axe"]= cobra_pca9685_v07.servo(myPCA9685,5, "HITEC HS-475HB")
brushless["gauche"] = cobra_pca9685_v07.brushless(myPCA9685,6)
brushless["droite"] = cobra_pca9685_v07.brushless(myPCA9685,7)

print("Prêt - Initialisation réalisée")

# Boucle_continue/principale
while True :
    nom_type = input("Donner type")
    if nom_type == "servo":
        nom_servo=input("Donner nom servo:")
        commande_angle_deg=int(input("Donner la commande d'angle du servomoteur en degres (entre -90 et 90):"))
        servo[nom_servo].cmd_angle_deg(commande_angle_deg)
    else:
        nom_brushless=input("Donner nom brushless:")
        commande_vitesse_pourcentage=int(input("Donner la commande de vitesse du moteur en pourcentage (entre -100 et 100):"))
        brushless[nom_brushless].cmd_vit_pourcent(commande_vitesse_pourcentage)
    
