from localisation import localiserSansTelemetre
import cv2
from picamera2 import Picamera2
from pyapriltags import Detector
import numpy as np
import smbus 
import math
import time

import smbus2
import cobra_pca9685_v12_COBRAQUAGE as pca9685 #nom du fichier global

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = pca9685.PCA9685(myi2cbus) # Initialisation du générateur de PWM

# Import des librairies pour les signaux logiques/numériques
from gpiozero import LED
import time

#numeros_moteurs = {"brushless": [1, 2, 3, 4, 5], "MCC": [6, 7]}

brushless = {}
mcc={}

# Instanciation des brushless et initialisation à vitesse nulle
brushless["d"] = pca9685.brushless(myPCA9685,1)
brushless["g"] = pca9685.brushless(myPCA9685,2)
brushless["c"] = pca9685.brushless(myPCA9685,3)
brushless["av"] = pca9685.brushless(myPCA9685,4)
brushless["ar"] = pca9685.brushless(myPCA9685,5)
mcc['t']= pca9685.MCC(myPCA9685,6,8,7)
mcc['p']= pca9685.MCC(myPCA9685,7,23,24)

# Instanciation des mcc et initialisation à vitesse nulle
#mcc['t']= pca9685.MCC(myPCA9685,6,8,7)
#mcc['p']= pca9685.MCC(myPCA9685,7,23,24)

#sens_mot11=GPIO8 - BROCHE 24
#sens_mot12=GPIO7 - BROCHE 26
#sens_mot21=GPIO23 - BROCHE 16
#sens_mot21=GPIO24 - BROCHE 18

print("Prêt - Initialisation réalisée")

class PID:
    def __init__(self, P, ITs, D, N, Ts):
        self.P = P
        self.ITs = ITs
        self.D = D
        self.N = N
        self.Ts = Ts
        self.erreur_pre=0
        self.int_pre=0
        self.deriv_pre=0
        self.a0=P+D*N

        self.a1=-2*(P+D*N)+P*N*Ts+ITs
        self.a2=(P+D*N)-P*N*Ts-ITs-ITs*Ts*N

        self.b0=1
        self.b1=N*Ts-2
        self.b2=1-N*Ts

    def compute(self, erreur):
        prop=self.P*erreur
        int=max(min(self.int_pre +self.ITs*self.erreur_pre,10),-10)
        deriv=self.D*self.N*(erreur-self.erreur_pre)-(self.N*self.Ts)*(self.deriv_pre)
        self.erreur_pre=erreur
        self.deriv_pre=deriv
        self.int_pre=int
        sortie=prop+int+deriv
        
        return sortie
    
    def compute2(self, measured_value):
        
        
        """Calcule la sortie PID en fonction de la valeur mesurée"""
        error = (self.consigne - (measured_value if measured_value <= 180 else measured_value - 360) + 180) % 360 - 180 

        # Terme proportionnel
        P = self.P * error

        # Terme intégral
        self.integral += error
        self.integral = max(min(self.integral, 100), -100)
        I = self.Ki * self.integral

        # Terme dérivé
        D = self.Kd * (error - self.previous_error)
        self.previous_error = error

        R=P
        # Sortie PID 
        output=R
        return output
    
    def compute3(self, error):
               
        """Calcule la sortie PID en fonction de l'erreur mesurée"""

        # Terme proportionnel
        P = self.P * error

        # Terme intégral
        self.integral += error
        self.integral = max(min(self.integral, 100), -100)
        I = self.Ki * self.integral

        # Terme dérivé
        D = self.Kd * (error - self.previous_error)
        self.previous_error = error

        R=P+D

        # Sortie PID (limitée entre 0 et 100 pour la vitesse du moteur)
        if R>0 : 
            output = max(min(R, 50), 20)
        else : 
            output=min(max(R,50),20)
        return output
while 1:
    brushless["d"].cmd_vit_pourcent(10)
    brushless["g"].cmd_vit_pourcent(-10)
    

    