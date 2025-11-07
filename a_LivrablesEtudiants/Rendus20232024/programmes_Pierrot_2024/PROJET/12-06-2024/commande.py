import time
import threading
import numpy as np
from statistics import fmean
import lib_moteurs_capteurs as lib
from pyPS4Controller.controller import Controller

import board
from adafruit_pca9685 import PCA9685

import RPi.GPIO as GPIO

#capt = lib.capteurs()

height = 0
yaw = 0
vit_yaw = 0
Omega = 0
yaw_mes = 0
yaw_mes_old = 0
offset_yaw = 0

ESCchiant = [[2000, 1150], [1, 0]]
BRUSHLESS = [[1539, 1024], [1, 0]]

def get_capt():
    yaw_liste = []
    global height
    global yaw
    global vit_yaw
    global yaw_mes
    global Omega
    global offset_yaw

    h_mes_old = capt.get()[0]
    t_mes = time.time()
        
    while True:
        yaw_mes_old = yaw_mes
        h_mes, a1, vit_yaw, yaw_mes = capt.get()
        if h_mes < 500 and h_mes > 10:
            if abs(h_mes_old-h_mes) < 40 or True:
                height = h_mes
                h_mes_old = h_mes
                t_mes = time.time()
            
        if len(yaw_liste) >= 10:
            del yaw_liste[0]

        if yaw_mes - yaw_mes_old < -180:
            Omega += 360
        elif yaw_mes - yaw_mes_old > 180:
            Omega -= 360
         
        yaw_liste.append(yaw_mes+Omega-180)
        yaw = fmean(yaw_liste) - offset_yaw
        if len(yaw_liste) == 1:
            offset_yaw = yaw

        #print(time.time(), height, yaw)

thread_capt = threading.Thread(target=get_capt, daemon=True)

f = 80
th = 0.05

consigne_queue = 0
consigne_alt = 150

ASSERV_ALT = True
ASSERV_YAW = True
ASSERV = True

i2c = board.I2C()
pca = PCA9685(i2c)

pca.frequency = f
pca.channels[2].duty_cycle = 0

GPIO.setup(13, GPIO.OUT)

def puissance_yaw(p):
    if p >= 0:
        GPIO.output(13, GPIO.LOW)
        pca.channels[2].duty_cycle = min(round(max(abs(p)-th, 0) * 65535), 65535)
    else:
        GPIO.output(13, GPIO.HIGH)
        pca.channels[2].duty_cycle = max(round(min(1-abs(p)+th, 1) * 65535), 0)

def puissance_avant(p):
    mu1, mu0 = ESCchiant[0][0] / 1e6, ESCchiant[0][1] / 1e6
    pca.channels[0].duty_cycle = round(((mu1-mu0)*p + mu0) * f * 65535)

def puissance_vert(p):
    mu1, mu0 = BRUSHLESS[0][0] / 1e6, BRUSHLESS[0][1] / 1e6
    pca.channels[1].duty_cycle = round(((mu1-mu0)*p + mu0) * f * 65535)

def setup_esc(n):
    pca.channels[n].duty_cycle = round(1000*1e-6*f*65535)


def asserv_vert():
    global height
    global consigne_alt
    global ASSERV_ALT
    H = 100
    while ASSERV_ALT:
        p = min(max((consigne_alt-height)/H, 0) + 0.18, 0.5)
        #print(p)
        puissance_vert(p)

th_asserv_vert = threading.Thread(target=asserv_vert, daemon=True)


def asserv_yaw():
    global yaw
    global consigne_queue

    Kp_yaw = 2
    Kd_yaw = 1
    Te = 0.01
    erreur_old = 0
    commande_old = 0
    a0 = Kp_yaw + 2*Kd_yaw/Te
    a1 = Kp_yaw - 2*Kd_yaw/Te
    
    while ASSERV_YAW:
        erreur = (consigne_queue - yaw)/180
        commande_queue = max(-1, min(1, a0*erreur + a1*erreur_old - commande_old))
        puissance_yaw(commande_queue)

        #print(consigne_queue, yaw, commande_queue)
        erreur_old = erreur
        commande_old = commande_queue
        time.sleep(Te)

th_asserv_yaw = threading.Thread(target=asserv_yaw, daemon=True)

list_angles = []
list_consignes = []
list_height = []

Kp = 0.04
Kd = 0.05

puissance_verticale = 0.6

def asserv():
    global yaw
    global vit_yaw
    global consigne_queue

    global height
    global consigne_alt
    global ASSERV_ALT

    global list_angles
    global list_consignes
    global Kp
    global Kd    

    global puissance_verticale
    
    H = 50

    erreur_old = 0
    commande_old = 0
    
    while ASSERV:
        erreur = (consigne_queue - yaw)
        derivee = - vit_yaw
        commande = Kp * erreur + Kd*derivee
        commande_queue = max(-1, min(1, commande))
        puissance_yaw(commande_queue)
        #list_angles.append(yaw)
        #list_consignes.append(Omega)
        #list_consignes.append(height)

        #print(consigne_queue, yaw, commande_queue)
        erreur_old = erreur
        commande_old = commande_queue
        time.sleep(0.01)
        p = min(max((consigne_alt-height)/H, 0) + 0.18, puissance_verticale)
        #print(time.time(), yaw, commande_queue)
        puissance_vert(p)
        
th_asserv = threading.Thread(target=asserv, daemon=True)


def demo_aller_retour():
    global ASSERV
    global consigne_queue
    global consigne_alt
    
    ASSERV = True
    th_asserv.start()

    print("phase 1")
    consigne_queue = 0
    consigne_alt = 150
    t = time.time()
    print(abs(yaw-consigne_queue), abs(vit_yaw), abs(t-time.time()))
    while (abs(yaw-consigne_queue) > 5 or abs(vit_yaw) > 5) and abs(t-time.time()) < 20:
         consigne_queue = 0
         puissance_avant(0)
         print("phase 2")
    puissance_avant(1)
    puissance_verticale = 0.8
    print("phase 3")
    time.sleep(10)
    puissance_avant(0)
    puissance_verticale = 0.6
    consigne_queue = -180
    t = time.time()
    print(abs(yaw-consigne_queue), abs(vit_yaw), abs(t-time.time()))
    while (abs(yaw-consigne_queue) > 5 or abs(vit_yaw) > 5) and abs(t-time.time()) < 20:
        consigne_queue = -180
        puissance_avant(0)
        print("phase 4")
    puissance_avant(1)
    puissance_verticale = 0.8
    print("phase 5")
    time.sleep(15)
    puissance_avant(0)
    puissance_verticale = 0.6
    consigne_queue = -360
    t = time.time()
    print(abs(yaw-consigne_queue), abs(vit_yaw), abs(t-time.time()))
    while (abs(yaw-consigne_queue) > 5 or abs(vit_yaw) > 5) and abs(t-time.time()) < 20:
        consigne_queue = -360
        puissance_avant(0)
        print("phase 6")
    print("terminé")

    ASSERV = False

    puissance_avant(0)
    puissance_yaw(0)
    puissance_alt(0)

th_demo = threading.Thread(target=demo_aller_retour, daemon=True)
    

n_x_press = 0
affichage = False

class MyController(Controller):

    def on_x_press(self):
        setup_esc(0)

    def on_x_release(self):
        pass

    def on_triangle_press(self):
        pass

    def on_triangle_release(self):
        pass

    def on_circle_press(self):
        pass

    def on_circle_release(self):
        pass

    def on_square_press(self):
        pass

    def on_square_release(self):
        pass

    def on_L1_press(self):
        pass

    def on_L1_release(self):
        pass

    def on_L2_press(self, value):
        pass

    def on_L2_release(self):
        pass

    def on_R1_press(self):
        pass

    def on_R1_release(self):
        pass

    def on_R2_press(self, value):
        pass

    def on_R2_release(self):
        pass

    def on_up_arrow_press(self):
        pass

    def on_up_down_arrow_release(self):
        pass

    def on_down_arrow_press(self):
        pass

    def on_left_arrow_press(self):
        pass

    def on_left_right_arrow_release(self):
        pass


    def on_right_arrow_press(self):
        pass

    def on_L3_up(self, value):
        pass

    def on_L3_down(self, value):
        pass

    def on_R3_up(self, value):
        pass

    def on_R3_down(self, value):
        pass

    def on_R3_left(self, value):
        pass

    def on_R3_right(self, value):
        pass

    def on_R3_release(self):
        pass

    def on_options_press(self):
        pass

    def on_options_release(self):
        pass
    
    def on_L2_press(self, value):
        puissance_vert(max(abs(value)/32767+0.18, 1))

    def on_L2_release(self):
        puissance_vert(0.18)

    def on_L3_right(self, value):
        puissance_yaw(abs(value)/32767)

    def on_L3_left(self, value):
        puissance_yaw(-abs(value)/32767)

    def on_L3_release(self):
        puissance_yaw(0)

    def on_L3_x_at_rest(self):
        puissance_yaw(0)

    def on_L3_y_at_rest(self):
        pass

    def on_R2_press(self, value):
        puissance_avant(abs(value)/32767)

    def on_R2_release(self):
        puissance_avant(0)

def stop():
    puissance_vert(0)
    puissance_yaw(0)
    puissance_avant(0)

#thread_capt.start()
#th_asserv_yaw.start()
def manette():
    MyController(interface="/dev/input/js0", connecting_using_ds4drv=False).listen()


