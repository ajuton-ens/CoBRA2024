from gpiozero import LED

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
                     {"ON_L": 0x12, "ON_H": 0x13, "OFF_L": 0x14, "OFF_H": 0x15},
                     {"ON_L": 0x16, "ON_H": 0x17, "OFF_L": 0x18, "OFF_H": 0x19},
                     {"ON_L": 0x1A, "ON_H": 0x1B, "OFF_L": 0x1C, "OFF_H": 0x1D},
                     {"ON_L": 0x1E, "ON_H": 0x1F, "OFF_L": 0x20, "OFF_H": 0x21},
                     {"ON_L": 0x22, "ON_H": 0x23, "OFF_L": 0x24, "OFF_H": 0x25},
                     {"ON_L": 0x26, "ON_H": 0x27, "OFF_L": 0x28, "OFF_H": 0x29}]

        self.PRE_SCALE = 0xFE # Numero du registre qui code la periode
        self.freqPWM_Hz = 50 # Frequence des PWM à 50Hz
        self.periodPWM = 1/self.freqPWM_Hz # Période à 20 millisecondes
        #Valeur théorique (avec formule datasheet) qui ne fonctionne pas à cause de l'imprécision de la clock 
            #self.PCA9685_PRE_SCALE_VALUE = (round(25*10**6/(4096*self.freqPWM_Hz)-1))  # configure la fréquence de la PWM sur tous les canaux
        #Valeur réelle fonctionnelle (+1)
        self.PCA9685_PRE_SCALE_VALUE = 123  # configure la fréquence de la PWM sur tous les canaux
        
        print("PRESCALE : ",self.PCA9685_PRE_SCALE_VALUE)

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
        points_off = temps_off_us*4095/(self.periodPWM*1e6)
        temps_H = points_off//256
        temps_L = points_off%256

        self.bus.write_byte_data(self.address_PCA9685,self.PWMs[num_PWM]["OFF_L"],int(temps_L))
        self.bus.write_byte_data(self.address_PCA9685,self.PWMs[num_PWM]["OFF_H"],int(temps_H))


class brushless:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_moteur : numero de la PWM de la PCA9685
    def __init__(self, PCA9685, num_moteur):
        self.num_moteur = num_moteur
        self.myPCA9685 = PCA9685
        self.valeur_repos_us = 1500 # valeur milieu de la commande en us=> pour laquelle la vitesse est nulle
        self.cmd_vit_pourcent(0) #initialisation à vitesse nulle
    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent < -100:
            vitesse_pourcent = -100
        if vitesse_pourcent > 100:
            vitesse_pourcent = 100
        if 0 < vitesse_pourcent :
            vitesse_pourcent = 4.5 + vitesse_pourcent #zone morte (commande )
        if 0 > vitesse_pourcent :
            vitesse_pourcent = -4.5+vitesse_pourcent   
        
        temps_etat_haut_us=self.valeur_repos_us+vitesse_pourcent*5 #100% correspond à +500us
        self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_moteur)

marques = { "FUTABA S3107":     {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286},
            "HITEC HS-475HB":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286}
            }


class MCC:
    def __init__(self,PCA9685,num_PWM_vitesse,pin_sens_AV,pin_sens_AR):
        
        self.num_PWM_vitesse = num_PWM_vitesse
        self.pin_sens_AV = LED(pin_sens_AV)
        self.pin_sens_AR = LED(pin_sens_AR)
        self.myPCA9685 = PCA9685
        self.pin_sens_AV.off()
        self.pin_sens_AR.off()
        self.valeur_repos_us = 1500 # valeur milieu de la commande en us=> pour laquelle la vitesse est nulle
        self.cmd_vit_pourcent(0)
        
    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent < -100:
            vitesse_pourcent = -100
        if vitesse_pourcent > 100:
            vitesse_pourcent = 100
        if 0 < vitesse_pourcent :
            self.pin_sens_AV.off()
            self.pin_sens_AR.on()
        if 0 > vitesse_pourcent :
            self.pin_sens_AV.on()
            self.pin_sens_AR.off()
            vitesse_pourcent=-vitesse_pourcent
        if vitesse_pourcent==0 :
            self.pin_sens_AV.off()
            self.pin_sens_AR.off()
        
        temps_etat_haut_us= 50 + vitesse_pourcent*190 #100% correspond à +19ms
        self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_PWM_vitesse)

 


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