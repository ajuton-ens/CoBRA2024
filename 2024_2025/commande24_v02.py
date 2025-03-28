#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:29:10 2025

@author: salybey
"""

# Derniere modif: 14/03/2025

import smbus2  
import time
import numpy as np
import warnings

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C

class PCA9685: #pour commander les sorties pwm
    def __init__(self, bus, address_PCA9685=0x40):
        
        self.address_PCA9685 = address_PCA9685
        self.bus=bus
       
       # INITIALISATION / DÉFINITION des registres
        self.MODE1 = 0x00  # self.REGISTRE = adresse_registre
        self.MODE2 = 0x01

        self.LED0_ON_L = 0x06
        self.LED0_ON_H = 0x07
        self.LED0_OFF_L = 0x08
        self.LED0_OFF_H = 0x09

        self.LED1_ON_L = 0x0A
        self.LED1_ON_H = 0x0B
        self.LED1_OFF_L = 0x0C
        self.LED1_OFF_H = 0x0D

        self.LED2_ON_L = 0x0E
        self.LED2_ON_H = 0x0F
        self.LED2_OFF_L = 0x10
        self.LED2_OFF_H = 0x11

        self.LED3_ON_L = 0x12
        self.LED3_ON_H = 0x13
        self.LED3_OFF_L = 0x14
        self.LED3_OFF_H = 0x15

        self.PRE_SCALE = 0xFE


        # CONFIGURATION des registres du PCA9685 et initialisation des moteurs/variateurs
        # write_byte_data prend trois arguments: l'adresse de l'appareil i2C, le nom de registre où on veut écrire, les données à écrire (byte/octet en hexadécimal)
        self.bus.write_byte_data(self.address_PCA9685,self.MODE1,0x10)
        self.bus.write_byte_data(self.address_PCA9685,self.PRE_SCALE,32) # 25MHz/(4096*frequence)-1 # attention, 25MHz pas precis
        self.bus.write_byte_data(self.address_PCA9685,self.MODE1,0x00)


        self.bus.write_byte_data(self.address_PCA9685,self.MODE2,0x04) 

        # Les quatre registres suivants permettent de définir précisément les intervalles d’allumage et d’extinction (largeur d'impulsion) pour chaque LED, ce qui permet de contrôler la position d’un moteur.
        # LED N°0
        self.bus.write_byte_data(self.address_PCA9685,self.LED0_ON_L,0)  
        self.bus.write_byte_data(self.address_PCA9685,self.LED0_ON_H,0x0)
        self.bus.write_byte_data(self.address_PCA9685,self.LED0_OFF_L,0) #0x153 pour ancien variateur
        self.bus.write_byte_data(self.address_PCA9685,self.LED0_OFF_H,0) #0x1 

        # LED N°1       
        self.bus.write_byte_data(self.address_PCA9685,self.LED1_ON_L,0) # 0x25 est la valeur hexadécimale de 37 : valeur médiane de 12 et 62 
        self.bus.write_byte_data(self.address_PCA9685,self.LED1_ON_H,0x0)
        self.bus.write_byte_data(self.address_PCA9685,self.LED1_OFF_L,0) #0x153 pour ancien variateur
        self.bus.write_byte_data(self.address_PCA9685,self.LED1_OFF_H,0) #0x1

        # LED N°2
        self.bus.write_byte_data(self.address_PCA9685,self.LED2_ON_L,0)
        self.bus.write_byte_data(self.address_PCA9685,self.LED2_ON_H,0x0)
        self.bus.write_byte_data(self.address_PCA9685,self.LED2_OFF_L,0)
        self.bus.write_byte_data(self.address_PCA9685,self.LED2_OFF_H,0)

        # LED N°3
        self.bus.write_byte_data(self.address_PCA9685,self.LED3_ON_L,0)
        self.bus.write_byte_data(self.address_PCA9685,self.LED3_ON_H,0x0)
        self.bus.write_byte_data(self.address_PCA9685,self.LED3_OFF_L,0)
        self.bus.write_byte_data(self.address_PCA9685,self.LED3_OFF_H,0)

        # PRE_SCALE (pour configurer la fréquence de la PWM (modulation de largeur d’impulsion) sur tous les canaux)
    def commande_moteur_vitesse_pourcentage(self,pourcent,num_moteur) :
        #valeur_milieu_periode=1227 # pour nouveau variateur
        
        valeur_repos = 4095*1.5/5 # 1.5

        #valeur_milieu_periode=0x140      # pour ancien variateur
        if pourcent < -200:
            pourcent = -200
        if pourcent > 200:
            pourcent = 200
        temp_off_us=valeur_repos+pourcent*4.095  #valeur milieu de la commande => pour laquelle la vitesse est nulle
        temps_H = temp_off_us//256
        temps_L = temp_off_us%256
        
        #print("fonction ecrire_temps_off_us appel")
        if num_moteur == 0 :
            self.bus.write_byte_data(self.address_PCA9685,self.LED0_OFF_L,int(temps_L))
            self.bus.write_byte_data(self.address_PCA9685,self.LED0_OFF_H,int(temps_H))
        if num_moteur == 1 :
            self.bus.write_byte_data(self.address_PCA9685,self.LED1_OFF_L,int(temps_L))
            self.bus.write_byte_data(self.address_PCA9685,self.LED1_OFF_H,int(temps_H))
        if num_moteur == 2 :
            self.bus.write_byte_data(self.address_PCA9685,self.LED2_OFF_L,int(temps_L))
            self.bus.write_byte_data(self.address_PCA9685,self.LED2_OFF_H,int(temps_H))
        if num_moteur == 3 :
            self.bus.write_byte_data(self.address_PCA9685,self.LED3_OFF_L,int(temps_L))
            self.bus.write_byte_data(self.address_PCA9685,self.LED3_OFF_H,int(temps_H))
        if num_moteur == 4 :
            self.bus.write_byte_data(self.address_PCA9685,self.LED4_OFF_L,int(temps_L))
            self.bus.write_byte_data(self.address_PCA9685,self.LED4_OFF_H,int(temps_H))
        


class brushless:
    def __init__(self, num_moteur):
        self.num_moteur = num_moteur
        myPCA9685.commande_moteur_vitesse_pourcentage(0,self.num_moteur)
    def cmd_vit_pourcent(self, vitesse_pourcent):
        myPCA9685.commande_moteur_vitesse_pourcentage(vitesse_pourcent,self.num_moteur)

myPCA9685 = PCA9685(myi2cbus) # Initialisation du générateur de PWM

mot = []
for i in range(0,4):
    mot.append(brushless(i)) # Initialisation du moteur
print("Prêt - Initialisation réalisée")

# Boucle_continue/principale
while True : 
    commande_vitesse_pourcentage=int(input("Donner la commande de vitesse du moteur en pourcentage (entre -100 et 100):"))
    numero_moteur=int(input("Donner numero moteur:"))
    
    mot[numero_moteur].cmd_vit_pourcent(commande_vitesse_pourcentage)