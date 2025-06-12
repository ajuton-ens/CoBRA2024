#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:29:10 2025

@author: salybey
"""

# Derniere modif: 28/03/2025

# https://web.archive.org/web/20250428194524/https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf
class PCA9685: #pour commander les sorties pwm
    def __init__(self, bus, address_PCA9685=0x60):
        # DÉFINITION des registres (valeurs initiales)
        self.address_PCA9685 = address_PCA9685
        self.bus=bus
        self.MODE1 = 0x00  # self.REGISTRE = adresse_registre
        self.MODE2 = 0x01

        # liste de dictionnaires. Chaque dictionnaire definit les registres d'une sortie PWM de la PCA9685
        self.PWMs = [{"ON_L": 0x06, "ON_H": 0x07, "OFF_L": 0x08, "OFF_H": 0x09},
                     {"ON_L": 0x0A, "ON_H": 0x0B, "OFF_L": 0x0C, "OFF_H": 0x0D},
                     {"ON_L": 0x0E, "ON_H": 0x0F, "OFF_L": 0x10, "OFF_H": 0x11},
                     {"ON_L": 0x12, "ON_H": 0x13, "OFF_L": 0x14, "OFF_H": 0x15},
                     {"ON_L": 0x16, "ON_H": 0x17, "OFF_L": 0x18, "OFF_H": 0x19},
                     {"ON_L": 0x1A, "ON_H": 0x1B, "OFF_L": 0x1C, "OFF_H": 0x1D},
                     {"ON_L": 0x1E, "ON_H": 0x1F, "OFF_L": 0x20, "OFF_H": 0x21},
                     {"ON_L": 0x22, "ON_H": 0x23, "OFF_L": 0x24, "OFF_H": 0x25},
                     {"ON_L": 0x26, "ON_H": 0x27, "OFF_L": 0x28, "OFF_H": 0x29}]

        self.PRE_SCALE = 0xFE # Numero du registre qui code la periode
        self.freqPWM_Hz = 50 # Frequence des PWM
        self.periodPWM = 1/self.freqPWM_Hz # 20 millisecondes
        #self.PCA9685_PRE_SCALE_VALUE = (round(25*10**6/(4096*self.freqPWM_Hz)-1)) #32  # configure la fréquence de la PWM sur tous les canaux
        self.PCA9685_PRE_SCALE_VALUE = 124#121

        


    def commande_moteur_vitesse_us(self,temps_off_us,num_PWM):
        points_off = temps_off_us*4095/(self.periodPWM*1e6)
        temps_H = points_off//256
        temps_L = points_off%256

    def reset(self): # software reset
        return


class brushless:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_moteur : numero de la PWM de la PCA9685
    def __init__(self, PCA9685, num_moteur, config):
        self.num_moteur = num_moteur
        self.myPCA9685 = PCA9685
        self.valeur_repos = config["valeur_repos_us"] # valeur milieu de la commande => pour laquelle la vitesse est nulle
        self.seuil_vitesse_neg_pourcent = config["seuil_vitesse_neg_pourcent"]
        self.seuil_vitesse_pos_pourcent = config["seuil_vitesse_pos_pourcent"]
        self.sens = config["sens"]
        self.coeff_multiplicatif = config["coeff_multiplicatif"]
        self.vitesse_max = config["vitesse_max"]
        self.vitesse_pourcent=0
        self.cmd_vit_pourcent(self.vitesse_pourcent)
    
    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent < -self.vitesse_max:
            vitesse_pourcent = -self.vitesse_max
        if vitesse_pourcent > self.vitesse_max:
            vitesse_pourcent = self.vitesse_max
        vitesse_pourcent = self.sens*vitesse_pourcent
        self.vitesse_pourcent = self.sens*vitesse_pourcent
        vitesse_pourcent *= self.coeff_multiplicatif
        if 0 < vitesse_pourcent and vitesse_pourcent < 1.5*self.seuil_vitesse_pos_pourcent:
            vitesse_pourcent = self.seuil_vitesse_pos_pourcent+vitesse_pourcent/2
        if 0 > vitesse_pourcent and vitesse_pourcent > 1.5*self.seuil_vitesse_neg_pourcent:
            vitesse_pourcent = self.seuil_vitesse_neg_pourcent+vitesse_pourcent/2
        temps_etat_haut_us=self.valeur_repos+vitesse_pourcent*0.5e3/100
        self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_moteur)

class servo:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_moteur : numero de la PWM de la PCA9685
    def __init__(self, PCA9685, num_moteur, config):
        self.num_moteur = num_moteur
        self.myPCA9685 = PCA9685
        self.valeur_repos_us = config["valeur_repos_us"]
        self.angle_min = config["angle_min"]
        self.angle_max = config["angle_max"]
        self.decalage_us_max = config["decalage_us_max"]
        self.angle_deg=0
        self.cmd_angle_deg(self.angle_deg)

    def cmd_angle_deg(self, angle):
        if angle < self.angle_min:
            angle = self.angle_min
        if angle > self.angle_max:
            angle = self.angle_max
        self.angle_deg = angle
        #temps_etat_haut_us=self.valeur_repos_us+angle*self.decalage_us_max*(10**3)/max(abs(self.angle_min), abs(self.angle_max))
        temps_etat_haut_us=int(1487+18.9*angle)
        if temps_etat_haut_us> 2000:
            temps_etat_haut_us=2000
        if temps_etat_haut_us<900:
            temps_etat_haut_us=900
        self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_moteur)


class MCC_2PWM:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_PWM1 : numero de la PWM de la PCA9685 connectee au pole gauche du MCC 
    # num_PWM2 : numero de la PWM de la PCA9685 connectee au pole droit  du MCC
    def __init__(self, PCA9685, num_PWM1, num_PWM2, config):
        self.num_PWM1 = num_PWM1
        self.num_PWM2 = num_PWM2
        self.myPCA9685 = PCA9685
        self.consigne_max_us = config["consigne_max_us"]
        self.consigne_min_us = config["consigne_min_us"]
        self.consigne_milieu_us = config["consigne_milieu_us"]
        # TODO : ADD SEUILS TO CMD_VIT_POURCENT
        self.vitesse_pourcent=0
        self.cmd_vit_pourcent(self.vitesse_pourcent)

    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent >= 0:
            if vitesse_pourcent > 100:
                vitesse_pourcent = 100
            self.vitesse_pourcent = vitesse_pourcent
            temps_off_us=self.vitesse_pourcent*self.myPCA9685.periodPWM*10**6/100
            #temps_off_us=self.consigne_milieu_us + (self.consigne_max_us-self.consigne_milieu_us)/100*self.vitesse_pourcent
            self.myPCA9685.commande_moteur_vitesse_us(0,self.num_PWM1)
            self.myPCA9685.commande_moteur_vitesse_us(temps_off_us,self.num_PWM2)
        else:
            if vitesse_pourcent < -100:
                vitesse_pourcent = -100
            self.vitesse_pourcent = vitesse_pourcent
            temps_off_us=-self.vitesse_pourcent*self.myPCA9685.periodPWM*10**6/100
            #temps_off_us=self.consigne_milieu_us + (self.consigne_milieu_us-self.consigne_min_us)/100*self.vitesse_pourcent
            self.myPCA9685.commande_moteur_vitesse_us(temps_off_us,self.num_PWM1)
            self.myPCA9685.commande_moteur_vitesse_us(0,self.num_PWM2)

class MCC_2PWM_pince:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_PWM1 : numero de la PWM de la PCA9685 connectee au pole gauche du MCC 
    # num_PWM2 : numero de la PWM de la PCA9685 connectee au pole droit  du MCC
    def __init__(self, PCA9685, num_PWM1, num_PWM2, config):
        self.num_PWM1 = num_PWM1
        self.num_PWM2 = num_PWM2
        self.myPCA9685 = PCA9685
        self.consigne_max_us = config["consigne_max_us"]
        self.consigne_min_us = config["consigne_min_us"]
        self.consigne_milieu_us = config["consigne_milieu_us"]
        self.vitesse_pourcent=0
        self.cmd_vit_pourcent(self.vitesse_pourcent)

    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent >= 0:
            if vitesse_pourcent > 100:
                vitesse_pourcent = 100
            self.vitesse_pourcent = vitesse_pourcent
            temps_off_us=(100-self.vitesse_pourcent)*self.myPCA9685.periodPWM*10**6/100
            self.myPCA9685.commande_moteur_vitesse_us(0,self.num_PWM1)
            self.myPCA9685.commande_moteur_vitesse_us(temps_off_us,self.num_PWM2)
        else:
            if vitesse_pourcent < -100:
                vitesse_pourcent = -100
            self.vitesse_pourcent = vitesse_pourcent
            temps_off_us=-self.vitesse_pourcent*self.myPCA9685.periodPWM*10**6/100
            self.myPCA9685.commande_moteur_vitesse_us(self.myPCA9685.periodPWM*10**6/100,self.num_PWM1)
            self.myPCA9685.commande_moteur_vitesse_us(temps_off_us,self.num_PWM2)

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
        self.vitesse_pourcent=0
        self.cmd_vit_pourcent(self.vitesse_pourcent)

    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent >= 0:
            if vitesse_pourcent > 100:
                vitesse_pourcent = 100
            self.vitesse_pourcent = vitesse_pourcent
            temps_off_us=vitesse_pourcent*4.095
            self.myPCA9685.commande_moteur_vitesse_us(self.myPCA9685.periodPWM,self.num_dirF)
            self.myPCA9685.commande_moteur_vitesse_us(0,self.num_dirB)
        else:
            if vitesse_pourcent < -100:
                vitesse_pourcent = -100
            self.vitesse_pourcent = vitesse_pourcent
            temps_off_us=-vitesse_pourcent*4.095
            self.myPCA9685.commande_moteur_vitesse_us(0,self.num_dirF)
            self.myPCA9685.commande_moteur_vitesse_us(self.myPCA9685.periodPWM,self.num_dirB)
        self.myPCA9685.commande_moteur_vitesse_us(temps_off_us,self.num_PWM)
