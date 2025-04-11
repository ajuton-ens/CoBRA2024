#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:29:10 2025

@author: salybey
"""

# Derniere modif: 28/03/2025

class PCA9685: #pour commander les sorties pwm
    def __init__(self, bus, address_PCA9685=0x40):
        
        self.address_PCA9685 = address_PCA9685
        self.bus=bus
       
       # INITIALISATION / DÉFINITION des registres
        self.MODE1 = 0x00  # self.REGISTRE = adresse_registre
        self.MODE2 = 0x01

        self.LEDS = [{"ON_L": 0x06, "ON_H": 0x07, "OFF_L": 0x08, "OFF_H": 0x09},
                     {"ON_L": 0x0A, "ON_H": 0x0B, "OFF_L": 0x0C, "OFF_H": 0x0D},
                     {"ON_L": 0x0E, "ON_H": 0x0F, "OFF_L": 0x10, "OFF_H": 0x11},
                     {"ON_L": 0x12, "ON_H": 0x13, "OFF_L": 0x14, "OFF_H": 0x15}]

        self.PRE_SCALE = 0xFE


        # CONFIGURATION des registres du PCA9685 et initialisation des moteurs/variateurs
        # write_byte_data prend trois arguments: l'adresse de l'appareil i2C, le nom de registre où on veut écrire, les données à écrire (byte/octet en hexadécimal)
        self.bus.write_byte_data(self.address_PCA9685,self.MODE1,0x10)
        self.bus.write_byte_data(self.address_PCA9685,self.PRE_SCALE,32) # 25MHz/(4096*frequence)-1 # attention, 25MHz pas precis
        self.bus.write_byte_data(self.address_PCA9685,self.MODE1,0x00)


        self.bus.write_byte_data(self.address_PCA9685,self.MODE2,0x04) 

        # Les N registres suivants permettent de définir précisément les intervalles d’allumage et d’extinction (largeur d'impulsion) pour chaque LED, ce qui permet de contrôler la position d’un moteur.
        for LED in self.LEDS:
            self.bus.write_byte_data(self.address_PCA9685, LED["ON_L"], 0)  
            self.bus.write_byte_data(self.address_PCA9685, LED["ON_H"], 0x0)
            self.bus.write_byte_data(self.address_PCA9685, LED["OFF_L"], 0x40) #0x153 pour ancien variateur
            self.bus.write_byte_data(self.address_PCA9685, LED["OFF_H"], 1) #0x1

    # PRE_SCALE (pour configurer la fréquence de la PWM (modulation de largeur d’impulsion) sur tous les canaux)
    def commande_moteur_vitesse_us(self,temps_off_us,num_moteur) :
        temps_H = temps_off_us//256
        temps_L = temps_off_us%256
        #print("fonction ecrire_temps_off_us appel")
        self.bus.write_byte_data(self.address_PCA9685,self.LEDS[num_moteur]["OFF_L"],int(temps_L))
        self.bus.write_byte_data(self.address_PCA9685,self.LEDS[num_moteur]["OFF_H"],int(temps_H))

    
        


class brushless:
    def __init__(self, PCA9685, num_moteur):
        self.num_moteur = num_moteur
        self.myPCA9685 = PCA9685
        self.myPCA9685.commande_moteur_vitesse_pourcentage(0,self.num_moteur)
        
    def cmd_vit_pourcent(self, vitesse_pourcent):
        self.myPCA9685.commande_moteur_vitesse_pourcentage(vitesse_pourcent,self.num_moteur)

class brushless:
    def __init__(self):
        self.num_moteur = num_moteur
        self.myPCA9685 = PCA9685
        self.myPCA9685.commande_moteur_vitesse_pourcentage(0,self.num_moteur)
        #valeur milieu de la commande => pour laquelle la vitesse est nulle
        self.valeur_repos = 4095*1.48/5 # 1.5
        #self.valeur_repos=1227     # pour nouveau variateur
        #self.valeur_repos=0x140    # pour ancien variateur

    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent < -100:
            vitesse_pourcent = -100
        if vitesse_pourcent > 100:
            vitesse_pourcent = 100
        temps_off_us=self.valeur_repos+vitesse_pourcent*4.095
        temps_H = temps_off_us//256 # todo : compenser les zones mortes avec un %+4 %-4 
        temps_L = temps_off_us%256
        
        temps_off_us=valeur_milieu_periode+vitesse_pourcent*4.095  #valeur milieu de la commande => pour laquelle la vitesse est nulle
        self.myPCA9685.commande_moteur_vitesse_pourcentage(temps_off_us,self.num_moteur)


truc notnot

def commande_moteur_vitesse_pourcentage(self,pourcent,num_moteur) :
        
        
        self.mytruc.commande_moteur_vitesse_us(temps_off_us)





""" PROGRAMME DE TEST

import smbus2  
import cobra_pca9685_v03

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C

myPCA9685 = cobra_pca9685_v03.PCA9685(myi2cbus) # Initialisation du générateur de PWM

mot = []
for i in range(0,4):
    mot.append(cobra_pca9685_v03.brushless(myPCA9685,i)) # Initialisation du moteur
print("Prêt - Initialisation réalisée")

# Boucle_continue/principale
while True : 
    numero_moteur=int(input("Donner numero moteur:"))
    commande_vitesse_pourcentage=int(input("Donner la commande de vitesse du moteur en pourcentage (entre -100 et 100):"))
    
    mot[numero_moteur].cmd_vit_pourcent(commande_vitesse_pourcentage)"

"""