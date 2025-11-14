from localisation import localiser
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
brushless["c"] = pca9685.brushless(myPCA9685,5)
brushless["av"] = pca9685.brushless(myPCA9685,4)
brushless["ar"] = pca9685.brushless(myPCA9685,3)
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

# Asservissement en hauteur init :
    
pidh = PID(-0.5,-0.02,-50,0.91,5.56e-02)

#pidavar = PID(0.06,0.003,0.2,cons)
points ={1:(3,1.5), 2: (3,4.5)} 

i = 1

#f=open("test_indiciel_X4.txt", "w")
x=0
y=0
z=0
lacet=0
consigneh=150
etat=0
while True : 
    print(f"on va vers le point {i}")
    destination = points[i]
    xd,yd,zd,td,rd,ld = localiser()
    if not(type(xd) == str):
        xd_old,yd_old,zd_old,td_old,rd_old,ld_old = xd,yd,zd,td,rd,ld
    else :
        xd,yd,zd,td,rd,ld = xd_old,yd_old,zd_old,td_old,rd_old,ld_old 
    consignea = np.arctan2((destination[0]-xd),(destination[1]-yd)) #en deg
    consignea *= (180/np.pi) # conversion en deg
    erreura = consignea-ld

    #borner l'erreur entre -+180 de l'erreur
    if erreura > 180:
        erreura = erreura - 360
    if erreura < -180:
        erreura = erreura + 360

    #calcul de la commande a partir de l'erreur
    #pidl = PID(0.8,0.0004,3.2,5.45,0.06) valeur initiale (Kp Ki Kd)
    #pidl = PID(0.06*0.8,0.15*0.0004,0.50*3.2,5.45,0.06) #valeur avant que salma partes
    pidl = PID(0.01*0.8,0.0004,2*3.2,2*5.45,0.06) 

    


    vitesse_tourner = pidl.compute(erreura*np.pi/180)
    if vitesse_tourner>40: # avec salma 60
        vitesse_tourner =40
    if vitesse_tourner<-30:
        vitesse_tourner = -30
    print("la commande de vitesse est : ", vitesse_tourner)
    
    brushless["av"].cmd_vit_pourcent(vitesse_tourner)
    brushless["ar"].cmd_vit_pourcent(0.650*vitesse_tourner)

    if abs(erreura)<50: #avant salma 20
        #distance_carree = (xd-destination[0])**2 + (yd-destination[1])**2
        brushless["d"].cmd_vit_pourcent(-0.650*15)
        brushless["g"].cmd_vit_pourcent(15)
        if abs(yd-destination[1]) <1.5:
            if i==2:
                i =1
            else:
                i +=1
            
        else :
            """
            if distance_carree >3*3:#freinage
                brushless["d"].cmd_vit_pourcent(0.650*13)
                brushless["g"].cmd_vit_pourcent(-13)"""
            

    else:
        brushless["d"].cmd_vit_pourcent(0)
        brushless["g"].cmd_vit_pourcent(0)

