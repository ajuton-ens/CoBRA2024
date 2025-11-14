from pyPS4Controller.controller import Controller
# Import des librairies pour les signaux PWM
import smbus2
import cobra_pca9685_v11_COBRAQUAGE as pca9685 #nom du fichier global

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = pca9685.PCA9685(myi2cbus) # Initialisation du générateur de PWM

# Import des librairies pour les signaux logiques/numériques
from gpiozero import LED

import time
import warnings

#numeros_moteurs = {"brushless": [1, 2, 3, 4, 5], "MCC": [6, 7]}

brushless = {}
mcc={}

# Instanciation des brushless et initialisation à vitesse nulle
brushless["d"] = pca9685.brushless(myPCA9685,1)
brushless["g"] = pca9685.brushless(myPCA9685,2)
brushless["c"] = pca9685.brushless(myPCA9685,3)
brushless["av"] = pca9685.brushless(myPCA9685,4)
brushless["ar"] = pca9685.brushless(myPCA9685,5)

# Instanciation des mcc et initialisation à vitesse nulle
mcc['t']= pca9685.MCC(myPCA9685,6,8,7)
mcc['p']= pca9685.MCC(myPCA9685,7,23,24)

#sens_mot11=GPIO23 - BROCHE 24
#sens_mot12=GPIO24 - BROCHE 26
#sens_mot21=GPIO8 - BROCHE 16
#sens_mot21=GPIO7 - BROCHE 18

#print("Prêt - Initialisation réalisée")


###################################################
#Programme de test de la manette PS4
##################################################


class MyController(Controller):
    
    def _init_(self, **kwargs):
        Controller._init_(self, **kwargs)
        
    def on_R2_press(self,value): # propulsion verticale vers HAUT 
        #print("La valeur de R2 est: ",value) 
        #if value<0 :
        #    value = 0
        value = value*5/3200 # Plage du joystick [-50%,50%] de la vitesse 
        #if value >100 :
        #    value = 100
        brushless["c"].cmd_vit_pourcent(-value)
    
    def on_R2_release(self): # arrêt aspiration verticale vers HAUT 
        brushless["c"].cmd_vit_pourcent(0)

    def on_L2_press(self,value): # aspiration verticale vers BAS 
        #if value<0 :
        #    value = 0
        value = value*5/3200 # Plage du joystick [-50%,50%] de la vitesse 
        #if value >100 :
        #    value = 100
        brushless["c"].cmd_vit_pourcent(-value)
    
    def on_L2_release(self): # arrêt aspiration verticale vers BAS 
        brushless["c"].cmd_vit_pourcent(0)
 
    def on_L3_x_at_rest(self):
        pass
        ##print("L3 au milieu")
        
    def on_R1_press(self):
        pass
        ##print("R1 enfoncé")
        
    def on_R1_release(self):
        pass
        ##print("R1 relaché")
    
    def on_R3_right(self,value): #tourner à droite
        #print("La valeur de L3 est: ",value)
        #if value<0 :
        #    value = 0
        value = value*5/3200
        #if value >100 :
        #    value = 100
        brushless["av"].cmd_vit_pourcent(value)
        brushless["ar"].cmd_vit_pourcent(value)

    def on_R3_left(self,value): #tourner à gauche
        #print("La valeur de L3 est: ",value)
        #if value>0 :
        #    value = 0
        value = value*5/3200
        #if value <-100 :
        #    value = -100
        brushless["av"].cmd_vit_pourcent(value)
        brushless["ar"].cmd_vit_pourcent(value)

    def on_L3_up(self,value): # marche avant
        #print("La valeur de R3_u est: ",value)
        #if value>0 :
        #    value = 0
        value = value*5/3200
        #if value <-100 :
        #    value = -100
        brushless["d"].cmd_vit_pourcent(value*0.8)
        brushless["g"].cmd_vit_pourcent(-value)
    
    def on_L3_down(self,value): # marche arrière
        #print("La valeur de R3_d est: ",value)
        #if value<0 :
        #    value = 0
        value = value*5/3200
        #if value >100 :
        #    value = 100
        brushless["g"].cmd_vit_pourcent(-value*0.8)
        brushless["d"].cmd_vit_pourcent(value)

    def on_L3_right(self,value): #déportation droite 
        #if value<0 :
        #    value = 0
        value = value*5/3200
        #if value >100 :
        #    value = 100
        brushless["av"].cmd_vit_pourcent(+value)
        brushless["ar"].cmd_vit_pourcent(-value)

    def on_L3_left(self,value): #déportation gauche
        #if value>0 :
        #    value = 0
        value = value*5/3200
        #if value <-100 :
        #    value = -100
        brushless["av"].cmd_vit_pourcent(+value)
        brushless["ar"].cmd_vit_pourcent(-value)

    def on_circle_press(self): #bouton arret d'urgence de tous les moteurs
        #print("O enfoncé")
        #brushless["d"].cmd_vit_pourcent(0)
        #brushless["g"].cmd_vit_pourcent(0)
        #brushless["c"].cmd_vit_pourcent(0)
        #brushless["av"].cmd_vit_pourcent(0)
        #brushless["ar"].cmd_vit_pourcent(0)
        mcc['t'].cmd_vit_pourcent(0)
        mcc['p'].cmd_vit_pourcent(0)
        
    def on_triangle_press(self): #ouverture pince 
        mcc['p'].cmd_vit_pourcent(70) #à 30% de la vitesse max
        #print("on_triangle_press")

    def on_triangle_release(self):#arrêt ouverture
        mcc['p'].cmd_vit_pourcent(0) 
        #print("on_triangle_release")

    def on_x_press(self): #fermeture pince
        mcc['p'].cmd_vit_pourcent(-70) #à -30% de la vitesse max
        #print("on_x_press")

    def on_x_release(self): #arrêt fermeture
        mcc['p'].cmd_vit_pourcent(0) 
        #print("on_x_release")

    def on_square_press(self): #ouverture pince 
        mcc['c'].cmd_vit_pourcent(0) #à 30% de la vitesse max
        #print("on_triangle_press")
    
    def on_up_arrow_press(self): # montée du treuil
        mcc['t'].cmd_vit_pourcent(100)
        #print("on_up_arrow_press")
    
    def on_up_arrow_release(self): # arrêt montée du treuil
        mcc['t'].cmd_vit_pourcent(0)
        #print("on_up_arrow_release")
    
    def on_down_arrow_press(self): # descente du treuil
        mcc['t'].cmd_vit_pourcent(-50)
        #print("on_down_arrow_press")

    def on_down_arrow_release(self): # arrêt descente du treuil
        mcc['t'].cmd_vit_pourcent(0) 
        #print("on_down_arrow_release")
        
    def on_R3_x_at_rest(self):
        pass


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()