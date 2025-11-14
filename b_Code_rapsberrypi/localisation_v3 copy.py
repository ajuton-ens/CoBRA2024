import math
from centrale_inirtielle import mesure_angles
from tf_luna import mesure_distance
from XY4 import Localisation
from picamera2 import Picamera2
import cobra_pca9685_v12_COBRAQUAGE as pca9685 #nom du fichier global
import time
import smbus2
myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = pca9685.PCA9685(myi2cbus) # Initialisation du générateur de PWM

listePoints3D = {93:(2.5, 2, 0) ,95:(3, 2.5,0),96:(2.5,3,0),97:(2, 2.5,0),84: (0.0, 14.0, 0.0), 85: (1.0, 14.0, 0.0), 86: (2.0, 14.0, 0.0), 87: (3.0, 14.0, 0.0), 88: (4.0, 14.0, 0.0), 89: (5.0, 14.0, 0.0),
                                78: (0.0, 13.0, 0.0), 79: (1.0, 13.0, 0.0), 80: (2.0, 13.0, 0.0), 81: (3.0, 13.0, 0.0), 82: (4.0, 13.0, 0.0), 83: (5.0, 13.0, 0.0),
                                72: (0.0, 12.0, 0.0), 73: (1.0, 12.0, 0.0), 74: (2.0, 12.0, 0.0), 75: (3.0, 12.0, 0.0), 76: (4.0, 12.0, 0.0), 77: (5.0, 12.0, 0.0),
                                66: (0.0, 11.0, 0.0), 67: (1.0, 11.0, 0.0), 68: (2.0, 11.0, 0.0), 69: (3.0, 11.0, 0.0), 70: (4.0, 11.0, 0.0), 71: (5.0, 11.0, 0.0),
                                60: (0.0, 10.0, 0.0), 61: (1.0, 10.0, 0.0), 62: (2.0, 10.0, 0.0), 63: (3.0, 10.0, 0.0), 64: (4.0, 10.0, 0.0), 65: (5.0, 10.0, 0.0),
                                54: (0.0, 9.0, 0.0), 55: (1.0, 9.0, 0.0), 56: (2.0, 9.0, 0.0), 57: (3.0, 9.0, 0.0), 58: (4.0, 9.0, 0.0), 59: (5.0, 9.0, 0.0),
                                48: (0.0, 8.0, 0.0), 49: (1.0, 8.0, 0.0), 50: (2.0, 8.0, 0.0), 51: (3.0, 8.0, 0.0), 52: (4.0, 8.0, 0.0), 53: (5.0, 8.0, 0.0),
                                42: (0.0, 7.0, 0.0), 43: (1.0, 7.0, 0.0), 44: (2.0, 7.0, 0.0), 45: (3.0, 7.0, 0.0), 46: (4.0, 7.0, 0.0), 47: (5.0, 7.0, 0.0),
                                36: (0.0, 6.0, 0.0), 37: (1.0, 6.0, 0.0), 38: (2.0, 6.0, 0.0), 39: (3.0, 6.0, 0.0), 40: (4.0, 6.0, 0.0), 41: (5.0, 6.0, 0.0),
                                30: (0.0, 5.0, 0.0), 31: (1.0, 5.0, 0.0), 32: (2.0, 5.0, 0.0), 33: (3.0, 5.0, 0.0), 34: (4.0, 5.0, 0.0), 35: (5.0, 5.0, 0.0),
                                24: (0.0, 4.0, 0.0), 25: (1.0, 4.0, 0.0), 26: (2.0, 4.0, 0.0), 27: (3.0, 4.0, 0.0), 28: (4.0, 4.0, 0.0), 29: (5.0, 4.0, 0.0),
                                18: (0.0, 3.0, 0.0), 19: (1.0, 3.0, 0.0), 20: (2.0, 3.0, 0.0), 21: (3.0, 3.0, 0.0), 22: (4.0, 3.0, 0.0), 23: (5.0, 3.0, 0.0),
                                12: (0.0, 2.0, 0.0), 13: (1.0, 2.0, 0.0), 14: (2.0, 2.0, 0.0), 15: (3.0, 2.0, 0.0), 16: (4.0, 2.0, 0.0), 17: (5.0, 2.0, 0.0),
                                6:  (0.0, 1.0, 0.0),  7: (1.0, 1.0, 0.0),  8: (2.0, 1.0, 0.0),  9: (3.0, 1.0, 0.0), 10: (4.0, 1.0, 0.0), 11: (5.0, 1.0, 0.0),
                                0:  (0.0, 0.0, 0.0),  1: (1.0, 0.0, 0.0),  2: (2.0, 0.0, 0.0),  3: (3.0, 0.0, 0.0),  4: (4.0, 0.0, 0.0),  5: (5.0, 0.0, 0.0)
                              }
tag = Localisation(listePoints3D)

def localiser():
    tangage, roulis, lacet = mesure_angles()
    d = mesure_distance()
    h = d*math.cos(tangage*math.pi/180)*math.cos(roulis*math.pi/180)
    xyl = tag.mesure()
    if xyl is None:
        return ("Aucun tag","Aucun tag",h,tangage,roulis,0)
    else:
        x,y,lacet = xyl
        offset = 4.2 # Calibration au début de chaque test
        lacet = lacet - offset
        if lacet<0:
            lacet = 360+lacet
        
        return(x,y,h,tangage,roulis,lacet)
       # print(x,y)
    #return (tangage,roulis,lacet)
    #return(h,d)
print(localiser())

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

pidh = PID(-0.5,-0.02,-50,0.91,5.56e-02)

brushless = {}
def test_indiciel_Z():
    f=open("test_indiciel1.txt", "w")
    brushless["c"] = pca9685.brushless(myPCA9685,3)
    t0 = time.time()
    while time.time()<(t0+20):
        print("Test en cours")
        t1=(time.time()-t0)
        mesure=localiser()[2]  
        if int(t1)%10<5:
            consigne=-70
            brushless["c"].cmd_vit_pourcent(consigne)
        else:
            consigne=50
            brushless["c"].cmd_vit_pourcent(consigne)
        f.write(f"{t1}\t{consigne}\t{mesure}\n")
    brushless["c"].cmd_vit_pourcent(0)
    f.close()
    return "Test terminé"

def test_indiciel_X():
    f=open("test_indiciel_X_3.txt", "w")
    brushless["c"] = pca9685.brushless(myPCA9685,3)
    brushless["d"] = pca9685.brushless(myPCA9685,1)
    brushless["g"] = pca9685.brushless(myPCA9685,2)
    brushless["c"].cmd_vit_pourcent(-20)
    t0 = time.time()
    while time.time()<(t0+20):
        print("Test en cours")
        t1=(time.time()-t0)
        mesure1=localiser()[0]
        mesure2=localiser()[1]  
        if int(t1)%10<5:
            consigne=-10
            brushless["d"].cmd_vit_pourcent_2_moteurs(consigne*0.8,-consigne)
        else:
            consigne=30
            brushless["d"].cmd_vit_pourcent_2_moteurs(consigne*0.8,-consigne)
        f.write(f"{t1}\t{consigne}\t{mesure1}\t{mesure2}\n")
    brushless["d"].cmd_vit_pourcent_2_moteurs(0,0)
    brushless["c"].cmd_vit_pourcent(0)
    f.close()
    return "Test terminé"

def test_indiciel_lacet():
    f=open("test_indiciel_lacet.txt", "w")
    brushless["c"] = pca9685.brushless(myPCA9685,3)
    brushless["av"] = pca9685.brushless(myPCA9685,4)
    brushless["ar"] = pca9685.brushless(myPCA9685,5)
    brushless["c"].cmd_vit_pourcent(-50)
    t0 = time.time()
    consigneh=200 #2m
    while time.time()<(t0+60):
        # PARTIE HAUTEUR

        mesures=localiser()
        z=mesures[2]  # hauteur
        x=mesures[0]
        y=mesures[1]
        lacet=mesures[5]
        erreur=consigneh-z
        vitesseh=pidh.compute(erreur)
        brushless["c"].cmd_vit_pourcent(vitesseh)
        print("Test en cours")
        if int(t1)%40<20:
            consigne=-20
            consigneav=consigne
            consignear=consigne
            if consigneav<0:
                consigneav=consigneav*0.7
            if consignear<0:
                consignear=consignear*0.7
            brushless["av"].cmd_vit_pourcent_2_moteurs(consigneav,consignear)
        else:
            consigne=20
            consigneav=consigne
            consignear=consigne
            if consigneav<0:
                consigneav=consigneav*0.7
            if consignear<0:
                consignear=consignear*0.7
            brushless["av"].cmd_vit_pourcent_2_moteurs(consigneav,consignear)
        f.write(f"{t1}\t{consigne}\t{lacet}\n")
    brushless["av"].cmd_vit_pourcent_2_moteurs(0,0)
    brushless["c"].cmd_vit_pourcent(0)
    f.close()
    return "Test terminé"

def test_indiciel_deportation():
    f=open("test_indiciel_deportation.txt", "w")
    brushless["c"] = pca9685.brushless(myPCA9685,3)
    brushless["av"] = pca9685.brushless(myPCA9685,4)
    brushless["ar"] = pca9685.brushless(myPCA9685,5)
    brushless["c"].cmd_vit_pourcent(-55)
    t0 = time.time()
    while time.time()<(t0+20):
        print("Test en cours")
        t1=(time.time()-t0)
        mesure1=localiser()[0]
        mesure2=localiser()[1]  
        if int(t1)%10<5:
            consigne=-20
            brushless["av"].cmd_vit_pourcent_2_moteurs(consigne,-consigne)
        else:
            consigne=20
            brushless["av"].cmd_vit_pourcent_2_moteurs(consigne,-consigne)
        f.write(f"{t1}\t{consigne}\t{mesure1}\t{mesure2}\n")
    brushless["av"].cmd_vit_pourcent_2_moteurs(0,0)
    brushless["c"].cmd_vit_pourcent(0)
    f.close()
    return "Test terminé"

# Exécution des tests
#A=test_indiciel_X()
#print(A)
