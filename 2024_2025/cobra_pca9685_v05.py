#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:29:10 2025

@author: salybey
"""

# Derniere modif: 28/03/2025

class PCA9685: #pour commander les sorties pwm
    def __init__(self, bus, address_PCA9685=0x40):
        # DÉFINITION des registres (valeurs initiales)
        self.address_PCA9685 = address_PCA9685
        self.bus=bus
        self.MODE1 = 0x00  # self.REGISTRE = adresse_registre
        self.MODE2 = 0x01

        # liste de dictionnaires. Chaque dictionnaire definit les registres d'une sortie PWM de la PCA9685
        self.PWMs = [{"ON_L": 0x06, "ON_H": 0x07, "OFF_L": 0x08, "OFF_H": 0x09},
                     {"ON_L": 0x0A, "ON_H": 0x0B, "OFF_L": 0x0C, "OFF_H": 0x0D},
                     {"ON_L": 0x0E, "ON_H": 0x0F, "OFF_L": 0x10, "OFF_H": 0x11},
                     {"ON_L": 0x12, "ON_H": 0x13, "OFF_L": 0x14, "OFF_H": 0x15}]

        self.PRE_SCALE = 0xFE # Numero du registre qui code la periode
        self.freqPWM_Hz = 50 # Frequence des PWM
        self.periodPWM = 1/self.freqPWM_Hz # 5 millisecondes
        self.PCA9685_PRE_SCALE_VALUE = (round(25*10**6/(4096*self.freqPWM_Hz)-1)) #32  # configure la fréquence de la PWM sur tous les canaux

        # CONFIGURATION des registres du PCA9685
        # write_byte_data prend trois arguments: l'adresse de l'appareil i2C, le nom de registre où on veut écrire, les données à écrire (byte/octet en hexadécimal)
        self.bus.write_byte_data(self.address_PCA9685,self.MODE1,0x10) # 
        self.bus.write_byte_data(self.address_PCA9685,self.PRE_SCALE,self.PCA9685_PRE_SCALE_VALUE) # 25MHz/(4096*freqPWM_Hz)-1 # attention, 25MHz pas precis
        self.bus.write_byte_data(self.address_PCA9685,self.MODE1,0x00) # 

        self.bus.write_byte_data(self.address_PCA9685,self.MODE2,0x04) 

        # Intervalles d’allumage et d’extinction (largeur d'impulsion) pour chaque PWM de self.PWMs.
        for PWM in self.PWMs: 
            self.bus.write_byte_data(self.address_PCA9685, PWM["ON_L"], 0)     
            self.bus.write_byte_data(self.address_PCA9685, PWM["ON_H"], 0x0)   
            self.bus.write_byte_data(self.address_PCA9685, PWM["OFF_L"], 0x40) #0x153 pour ancien variateur
            self.bus.write_byte_data(self.address_PCA9685, PWM["OFF_H"], 1) #0x1

    def commande_moteur_vitesse_us(self,temps_off_us,num_PWM) :
        temps_H = temps_off_us//256
        temps_L = temps_off_us%256

        self.bus.write_byte_data(self.address_PCA9685,self.PWMs[num_PWM]["OFF_L"],int(temps_L))
        self.bus.write_byte_data(self.address_PCA9685,self.PWMs[num_PWM]["OFF_H"],int(temps_H))


class brushless:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_moteur : numero de la PWM de la PCA9685
    def __init__(self, PCA9685, num_moteur):
        self.num_moteur = num_moteur
        self.myPCA9685 = PCA9685
        self.valeur_repos = 4095*1.5/5 # valeur milieu de la commande => pour laquelle la vitesse est nulle
        #self.valeur_repos=1227     # pour nouveau variateur
        #self.valeur_repos=0x140    # pour ancien variateur
        self.cmd_vit_pourcent(0)
    
    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent < -100:
            vitesse_pourcent = -100
        if vitesse_pourcent > 100:
            vitesse_pourcent = 100
        if 0 < vitesse_pourcent and vitesse_pourcent < 9:
            vitesse_pourcent = 4.5+vitesse_pourcent/2
        if 0 > vitesse_pourcent and vitesse_pourcent > -9:
            vitesse_pourcent = -4.5+vitesse_pourcent/2    
        
        temps_etat_haut_us=self.valeur_repos+vitesse_pourcent*4.095
        self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_moteur)

class servo:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_moteur : numero de la PWM de la PCA9685
    def __init__(self, PCA9685, num_moteur):
        self.num_moteur = num_moteur
        self.myPCA9685 = PCA9685
        #valeur milieu de la commande => pour laquelle la vitesse est nulle
        self.valeur_repos_us = 1.5*10**3
        self.cmd_angle_deg(0)

    def cmd_angle_deg(self, angle):
        if angle < -90:
            angle = -90
        if angle > 90:
            angle = 90
        temps_etat_haut_us=self.valeur_repos_us+angle*0.5*(10**3)/90
        self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_moteur)


class MCC_2PWM:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_PWM1 : numero de la PWM de la PCA9685 connectee au pole gauche du MCC 
    # num_PWM2 : numero de la PWM de la PCA9685 connectee au pole droit  du MCC
    def __init__(self, PCA9685, num_PWM1, num_PWM2):
        self.num_PWM1 = num_PWM1
        self.num_PWM2 = num_PWM2
        self.myPCA9685 = PCA9685
        self.cmd_vit_pourcent(0)

    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent >= 0:
            if vitesse_pourcent > 100:
                vitesse_pourcent = 100
            temps_off_us=self.vitesse_pourcent*4.095
            self.myPCA9685.commande_moteur_vitesse_us(0,self.num_PWM1)
            self.myPCA9685.commande_moteur_vitesse_us(temps_off_us,self.num_PWM2)
        else:
            if vitesse_pourcent < -100:
                vitesse_pourcent = -100
            temps_off_us=-self.vitesse_pourcent*4.095
            self.myPCA9685.commande_moteur_vitesse_us(temps_off_us,self.num_PWM1)
            self.myPCA9685.commande_moteur_vitesse_us(0,self.num_PWM2)


class MCC_3PWM:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_dirF : numero de la PWM de la PCA9685 connectee au signal de direction avant
    # num_dirB : numero de la PWM de la PCA9685 connectee au signal de direction arriere
    # num_PWM  : numero de la PWM de la PCA9685 connectee a la modulation de vitesse
    def __init__(self, PCA9685, num_dirF, num_dirB, num_PWM):
        self.num_dirF = num_dirF # direction PWM Forward
        self.num_dirB = num_dirB # direction PWM Backward
        self.num_PWM = num_PWM # speed value PWM
        self.myPCA9685 = PCA9685
        self.cmd_vit_pourcent(0)

    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent >= 0:
            if vitesse_pourcent > 100:
                vitesse_pourcent = 100
            temps_off_us=vitesse_pourcent*4.095
            self.myPCA9685.commande_moteur_vitesse_us(self.myPCA9685.periodPWM,self.num_dirF)
            self.myPCA9685.commande_moteur_vitesse_us(0,self.num_dirB)
        else:
            if vitesse_pourcent < -100:
                vitesse_pourcent = -100
            temps_off_us=-vitesse_pourcent*4.095
            self.myPCA9685.commande_moteur_vitesse_us(0,self.num_dirF)
            self.myPCA9685.commande_moteur_vitesse_us(self.myPCA9685.periodPWM,self.num_dirB)
        self.myPCA9685.commande_moteur_vitesse_us(temps_off_us,self.num_PWM)




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