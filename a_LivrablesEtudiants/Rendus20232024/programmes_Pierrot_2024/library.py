from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)
import warnings
import time

HS_225BB = [[1840, 1107, 857], [270, 0, -90]]
MOTOR_YAW = [[1829, 1525, 1453, 1112], [1, 0, 0, -1]]
BRUSHLESS = [[1539, 1024], [1, 0]]

def set_pulse_width(i, pw):
    """Envoie le signal PWM de largeur d'impulsion pw sur le channel i"""
    thr = pulse_width_to_thr(pw)
    kit.continuous_servo[i].throttle = thr

def pulse_width_to_thr(pw):
    """Convertit un signal en largeur d'impulsion en sa valeur de throttle equivalente."""
    return (pw - 1445)/(2170 - 1445)
   
def impulsion_commande_servo(SERVO, angle):
    """Calcule la largeur d'impulsion correspondant à l'angle angle pour le servomoteur SERVO"""
    pw = 0
    if angle > SERVO[1][0]:
        pw = SERVO[0][0]
        warnings.warn("Angle trop important !")
    elif angle <= SERVO[1][0] and angle > SERVO[1][1]:
        pw = (angle-SERVO[1][1])/(SERVO[1][0]-SERVO[1][1])*(SERVO[0][0]-SERVO[0][1]) + SERVO[0][1]
    elif angle <= SERVO[1][1] and angle >= SERVO[1][2]:
        pw = (angle-SERVO[1][2])/(SERVO[1][1]-SERVO[1][2])*(SERVO[0][1]-SERVO[0][2]) + SERVO[0][2]
    else :
        pw = SERVO[0][2]
        warnings.warn("Angle trop faible !")
    return pw
    
def impulsion_commande_moteur(MOTOR, fraction_puissance):
    """Calcule la largeur d'impulsion correspondant à la fraction_puissancesance fraction_puissance pour le moteur MOTOR"""
    if len(MOTOR[0]) == 4:
        if fraction_puissance > MOTOR[1][0]:
            pw = MOTOR[0][0]
            warnings.warn("fraction_puissancesance trop importante !")
        elif fraction_puissance <= MOTOR[1][0] and fraction_puissance > MOTOR[1][1]:
            pw = (fraction_puissance-MOTOR[1][1])/(MOTOR[1][0]-MOTOR[1][1])*(MOTOR[0][0]-MOTOR[0][1]) + MOTOR[0][1]
        elif fraction_puissance <= MOTOR[1][2] and fraction_puissance >= MOTOR[1][3]:
            pw = (fraction_puissance-MOTOR[1][3])/(MOTOR[1][2]-MOTOR[1][3])*(MOTOR[0][2]-MOTOR[0][3]) + MOTOR[0][3]
        else :
            pw = MOTOR[0][3]
            warnings.warn("fraction_puissancesance trop faible !")
    else :
        if fraction_puissance > MOTOR[1][0]:
            pw = MOTOR[0][0]
            warnings.warn("fraction_puissancesance trop importante !")
        elif fraction_puissance <= MOTOR[1][0] and fraction_puissance > MOTOR[1][1]:
            pw = (fraction_puissance-MOTOR[1][1])/(MOTOR[1][0]-MOTOR[1][1])*(MOTOR[0][0]-MOTOR[0][1]) + MOTOR[0][1]
        else:
            pw = MOTOR[0][2]
            warnings.warn("fraction_puissancesance trop faible !")
        
    return pw

def init(i):
    set_pulse_width(i, 2000)
    time.sleep(2)
    set_pulse_width(i, 1000)
    time.sleep(3)