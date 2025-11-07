#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  2 11:49:31 2025

@author: salybey
"""

from pyPS4Controller.controller import Controller

import time
import smbus  
import time
import numpy as np
#from adafruit_servokit import ServoKit #pour utiliser composant PCA9685
#kit = ServoKit(channels=16)
import warnings
from time import sleep
import smbus2
import cobra_pca9685_v09_Cobrapid
import pygame as p

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = cobra_pca9685_v09_Cobrapid.PCA9685(myi2cbus) # Initialisation du générateur de PWM

numeros_moteurs = {"brushless": [ 1, 2,3, 4], "MCC": [[6, 7], [7, 8]]}

brushless = {}

brushless["d"] = cobra_pca9685_v09_Cobrapid.brushless(myPCA9685,1)
brushless["g"] = cobra_pca9685_v09_Cobrapid.brushless(myPCA9685,2)
brushless["av"] = cobra_pca9685_v09_Cobrapid.brushless(myPCA9685,3)
brushless["ar"] = cobra_pca9685_v09_Cobrapid.brushless(myPCA9685,4)

print("Prêt - Initialisation réalisée")


###################################################
#Programme de test de la manette PS4
##################################################


class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        
    def on_R2_press(self,value): # moteur central
        pass
    

    def on_R2_release(self):
        pass
 
    def on_L3_x_at_rest(self):
        pass
        #print("L3 au milieu")
        
    def on_R1_press(self):
        pass
        #print("R1 enfoncé")
        
    def on_R1_release(self):
        pass
        #print("R1 relaché")
    
    def on_L3_right(self,value): #tourner à droite
        
        if value<0 :
            value = 0
        value = value*10/3200
        if value >100 :
            value = 100
        print("La valeur de L3 est: ",value)
        brushless["g"].cmd_vit_pourcent(value)
        brushless["d"].cmd_vit_pourcent(-value)

    def on_L3_left(self,value): #tourner à gauche
        
        if value>0 :
            value = 0
        value = value*10/3200
        if value <-100 :
            value = -100
        print("La valeur de L3 est: ",value)
        brushless["g"].cmd_vit_pourcent(value)
        brushless["d"].cmd_vit_pourcent(-value)

    def on_R3_up(self,value): # marche avant
        
        if value>0 :
            value = 0
        value = value*5/3200
        if value <-50 :
            value = -50
        #print("La valeur de R3_u est: ",value)
        brushless["av"].cmd_vit_pourcent(value)
        brushless["ar"].cmd_vit_pourcent(value)
    
    def on_R3_down(self,value): # marche arrière
        
        if value<0 :
            value = 0
        value = value*5/3200
        if value >50 :
            value = 50
        #print("La valeur de R3_d est: ",value)
        brushless["av"].cmd_vit_pourcent(-value)
        brushless["ar"].cmd_vit_pourcent(-value)
        
    def on_L2_press(self, value):
        pass
        
        
    def on_L2_release(self):
        pass
        
        
    def on_x_press(self):
        brushless['ar'].stop_mot()
        brushless['av'].stop_mot()
        brushless['g'].stop_mot()
        brushless['d'].stop_mot()
        
    def on_circle_press(self):
        brushless["ar"].cmd_vit_pourcent(0)
        brushless["av"].cmd_vit_pourcent(0)
        brushless["g"].cmd_vit_pourcent(0)
        brushless["d"].cmd_vit_pourcent(0)

    def on_R3_x_at_rest(self):
        pass

    def on_R3_right(self,value):
        pass
    def on_R3_left(self,value):
        pass
    def on_L3_up(self,value):
        pass
    def on_L3_down(self,value):
        pass
    def on_L3_y_at_rest(self):
        pass
    def on_R3_y_at_rest(self):
        pass

#La bibliothèque que nous avons écrite se base sur la bibliothèque adafruit_servokit





controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()


