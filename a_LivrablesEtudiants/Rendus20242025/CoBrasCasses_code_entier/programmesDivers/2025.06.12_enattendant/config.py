import numpy as np
import FAKE_LIB.cobra_pca9685 as pca9685
import FAKE_LIB.smbus2 as smbus2


## CONFIG INDICES DES ELEMENTS DES MESURES ##

X_INDEX = 0
Y_INDEX = 1
Z_INDEX = 2
HEADING_INDEX = 3
PITCH_INDEX = 4
ROLL_INDEX = 5


## CONFIG INDICES DES ELEMENTS DE LA MATRICE D'ETAT
TIME_INDEX                = 0
MESURES_INDEX             = 1
CONSIGNES_POSITIONS_INDEX = 2
ERREURS_INDEX             = 3
COMMANDES_FORCES_INDEX    = 4

## CONFIG CONSTANTES DES MOTEURS ##
DROITE_INDEX  = 0
GAUCHE_INDEX  = 1
AXE_INDEX     = 2
CERCEAU_INDEX = 3

NB_AXES = 6
NB_ECHANTILLONS  = 20
NB_ELEMENTS_MATRICE_ETAT = 5
NB_ACTIONNEURS = 4


## CONFIG ASSERV ##
Kp = np.array([1,1,1,1,1,1])
Td = np.array([1,1,1,1,1,1])
Ti = np.array([1000,1000,1000,1000,1000,1000])


## CONFIG CONSIGNES POSITIONS ##
Consignes_Positions = np.array((NB_AXES,NB_ECHANTILLONS))
Consignes_Positions[Z_INDEX,:] = 40


## CONFIG COMMANDES FORCES ##
Saturation_Efforts=[[] for i in range(NB_AXES)]
Saturation_Efforts[X_INDEX] = {}
Saturation_Efforts[Y_INDEX] = {}
Saturation_Efforts[Z_INDEX] = {}
Saturation_Efforts[HEADING_INDEX] = {}
Saturation_Efforts[PITCH_INDEX] = {}
Saturation_Efforts[ROLL_INDEX] = {}

Saturation_Efforts[X_INDEX]["min"] = -40
Saturation_Efforts[X_INDEX]["max"] = 40

Saturation_Efforts[Y_INDEX]["min"] = -40
Saturation_Efforts[Y_INDEX]["max"] = 40

Saturation_Efforts[Z_INDEX]["min"] = -40
Saturation_Efforts[Z_INDEX]["max"] = 40

Saturation_Efforts[HEADING_INDEX]["min"] = -40
Saturation_Efforts[HEADING_INDEX]["max"] = 40

Saturation_Efforts[PITCH_INDEX]["min"] = -40
Saturation_Efforts[PITCH_INDEX]["max"] = 40

Saturation_Efforts[ROLL_INDEX]["min"] = -40
Saturation_Efforts[ROLL_INDEX]["max"] = 40


## CONFIG MOTEURS ##
brushless_g_config = { "propulsion":   {"valeur_repos_us": 1.52*10**3, "seuil_vitesse_neg_pourcent": -10, "seuil_vitesse_pos_pourcent": 10, "sens": 1, "coeff_multiplicatif":1, "vitesse_max":50}
            }

brushless_d_config = { "propulsion":   {"valeur_repos_us": 1.52*10**3, "seuil_vitesse_neg_pourcent": -10, "seuil_vitesse_pos_pourcent": 10, "sens": -1, "coeff_multiplicatif":1, "vitesse_max":50}
            }

MCC2_config = { "lent":   {"consigne_milieu_us": 1500, "consigne_min_us": 1000, "consigne_max_us": 2000},
               "pince":   {"consigne_milieu_us": 1500, "consigne_min_us": 1000, "consigne_max_us": 2500}
            }

#FUTABA S3107 : 2.37ms correspond a 0deg du systeme.
#FUTABA S3107 : 1.92ms correspond a 90deg du systeme.
#FUTABA S3107 : 1.38ms correspond a 180deg du systeme.

servo_config = { "cerceau":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286},
                 "axe":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286}
            }

#-30 0 920us
#24 180 1.94us


## INITIALISATIONS MOTEURS ##

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = pca9685.PCA9685(myi2cbus) # Initialisation du générateur de PWM

brushless = {}
servo = {}
mcc_2pwm = {}

servo["cerceau"]= pca9685.servo(myPCA9685,4, servo_config["cerceau"])
servo["axe"]= pca9685.servo(myPCA9685,5, servo_config["axe"])
brushless["gauche"] = pca9685.brushless(myPCA9685,6,brushless_g_config["propulsion"])
brushless["droite"] = pca9685.brushless(myPCA9685,7,brushless_d_config["propulsion"])
mcc_2pwm["treuil"] = pca9685.MCC_2PWM(myPCA9685,0,1,MCC2_config["lent"])
mcc_2pwm["pince"] = pca9685.MCC_2PWM(myPCA9685,2,3,MCC2_config["pince"])

