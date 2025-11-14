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
        P = self.Kp * error

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
        P = self.Kp * error

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
pidl = PID(0.8,0.0004,3.2,5.45,0.06)
pidx = PID(-35.3,-0.982,-252.7,3.448,0.11)
pidy = PID(-35.3,-0.982,-252.7,3.448,0.11)


#xc = int(input("donner abcisse consigne:"))
# yc = int(input("donner ordonée consigne:"))

# x,y,z,tangage,roulis,lacet = localiser()

# x0=localiser()[0]
# y0=localiser()[1]
# a0=localiser()[5]

# angleradc=math.atan2(xc,yc)
# angledegc=math.degrees(angleradc)
#cons=90
#pid = PID(0.06,0.003,0.2,cons)
#pidgd= PID(0.06,0.003,0.2,cons)
#pidavar = PID(0.06,0.003,0.2,cons)
t0=time.time()

#f=open("test_indiciel_X4.txt", "w")
x=0
y=0
z=0
lacet=0
consigneh=150
etat=0
while True : 
    # PARTIE HAUTEUR
    
    xold=x
    yold=y
    zold=z
    lacetold=lacet
    x,y,z,tangage,roulis,lacet = localiser()
    if type(x)==str:
        x=xold
        y=yold
        z=zold
    erreur=consigneh-z
    vitesseh=pidh.compute(erreur)
    #print("z ",z,vitesseh)
    brushless["c"].cmd_vit_pourcent(vitesseh)
"""
    if (z<100 and etat>=1) or etat==2 : # si on est en dessous de 1m
        #t1=0
        # if z.round() = 99: 
        t1=time.time()
        # else :
        #     t1 = 200
        etat=2
        mcc['t'].cmd_vit_pourcent(-100) #descente
        print(time.time()-t1)
        #time.sleep(4)
        if time.time()-t1>4:
            mcc['t'].cmd_vit_pourcent(0)
            mcc['p'].cmd_vit_pourcent(100) #ouverture
        if time.time()-t1>10:
            #time.sleep(5)
            mcc['p'].cmd_vit_pourcent(0)
        consigneh=200
    
    # PARTIE X 
    consignex=2.5 #en m
    erreurx=consignex-x
    if etat==0 and y<3 :
        etat=1 
        consigneh=100
    vitessex=pidx.compute(erreurx)
    if vitessex > 50:
        vitessex = 50
    if vitessex < -50:
        vitessex = -50
    vitesseg=-vitessex
    vitessed=vitessex
    if vitessex<0:
        vitessed=vitessed*0.7
    else:
        vitesseg=vitesseg*0.7
    brushless["d"].cmd_vit_pourcent_2_moteurs(vitessed,vitesseg)

    # partie LACET
    consignea=90 #en deg
    # if int(t1)%20<10:
    #     consignex=-20
    #     brushless["d"].cmd_vit_pourcent_2_moteurs(consignex*0.7,-consignex)
    # else:
    #     consignex=50
    #     brushless["d"].cmd_vit_pourcent_2_moteurs(consignex,-consignex*0.7)

    angle=localiser()[5]
    erreura=consignea-angle
    if erreura > 180:
        erreura = erreura - 360
    if erreura < -180:
        erreura = erreura + 360
    commandel=pidl.compute(erreura)
    if commandel > 40:
        commandel = 40
    if commandel < -40:
        commandel = -40
    
    # PARTIE Y 
    consigney=2.48 #en m
    erreury=consigney-y
    commandey=pidy.compute(erreury)
    if commandey > 40:
        commandey = 40
    if commandey < -40:
        commandey = -40
    commandeav=commandel+commandey
    commandear=commandel-commandey
    if commandeav<0:
        commandeav=commandeav*0.7
    if commandear<0:
        commandear=commandear*0.7
    brushless["av"].cmd_vit_pourcent_2_moteurs(commandeav,commandear)
    """
    #f.write(f"{t1}\t{consignex}\t{x}\t{y}\n")

    # 
    #dx=xc-x
    #dy=yc-y
    #anglerad=math.atan2(dx,dy)
    #angledeg=math.degrees(anglerad)
    #zone=0
    #if zone == 0 : 
        #vitesse=pid.compute2(angle)
        #print(angle,vitesse)
        #brushless["av"].cmd_vit_pourcent(vitesse)
        #brushless["ar"].cmd_vit_pourcent(vitesse)

    #   distance=math.sqrt(dx**2+dy**2)
    #    if distance < 1.5 : 
    #       zone=1
    #   if abs(angledeg-angledegc) < 5 :
    #     vitesse2=pid.compute3(distance)
    #     brushless["d"].cmd_vit_pourcent(vitesseh)
    #     brushless["g"].cmd_vit_pourcent(vitesseh)
    #     brushless["av"].cmd_vit_pourcent(vitesseh)
    #     brushless["ar"].cmd_vit_pourcent(vitesseh)

    # else: 
        # vitesse2=pid.compute3(distance)
    #     brushless["d"].cmd_vit_pourcent(vitesse2)
    #     brushless["g"].cmd_vit_pourcent(vitesse2)
