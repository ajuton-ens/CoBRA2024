import motor_lib.cobra_pca9685 as pca9685
import smbus2

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = pca9685.PCA9685(myi2cbus) # Initialisation du générateur de PWM


brushless_g_config = { "propulsion":   {"valeur_repos_us": 1.52*10**3, "seuil_vitesse_neg_pourcent": -10, "seuil_vitesse_pos_pourcent": 10, "sens": -1, "coeff_multiplicatif":-1, "vitesse_max":50}
            }

brushless_d_config = { "propulsion":   {"valeur_repos_us": 1.52*10**3, "seuil_vitesse_neg_pourcent": -10, "seuil_vitesse_pos_pourcent": 10, "sens": -1, "coeff_multiplicatif":1, "vitesse_max":50}
            }

MCC2_config = { "lent":   {"consigne_milieu_us": 1500, "consigne_min_us": 1000, "consigne_max_us": 2000},
               "pince":   {"consigne_milieu_us": 2000, "consigne_min_us": 1500, "consigne_max_us": 2500}
            }

#FUTABA S3107 : 2.37ms correspond a 0deg du systeme.
#FUTABA S3107 : 1.92ms correspond a 90deg du systeme.
#FUTABA S3107 : 1.38ms correspond a 180deg du systeme.

servo_config = { "cerceau":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286},
                 "axe":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286}
            }

#-30 0 920us
#24 180 1.94us

brushless = {}
servo = {}
mcc_2pwm = {}

servo["cerceau"]= pca9685.servo(myPCA9685,4, servo_config["cerceau"])
servo["axe"]= pca9685.servo(myPCA9685,5, servo_config["axe"])
brushless["gauche"] = pca9685.brushless(myPCA9685,6,brushless_g_config["propulsion"])
brushless["droite"] = pca9685.brushless(myPCA9685,7,brushless_d_config["propulsion"])
mcc_2pwm["treuil"] = pca9685.MCC_2PWM(myPCA9685,0,1,MCC2_config["lent"])
mcc_2pwm["pince"] = pca9685.MCC_2PWM_pince(myPCA9685,2,3,MCC2_config["pince"])