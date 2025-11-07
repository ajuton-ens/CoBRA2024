import cv2
from picamera2 import Picamera2
from pyapriltags import Detector
import numpy as np
import math

tag=Tag()


lidar = LidarTFLuna()


# Asservissement en hauteur init :   
consigneh = int(input("donner consigne hauteur:"))
pidh = PID(0.5,0.1,0.05,consigneh)

xc = int(input("donner abcisse consigne:"))
yc = int(input("donner ordonée consigne:"))

tag=Tag()

x0=tag.localisation()[0]
y0=tag.localisation()[1]
a0=tag.localisation()[3]

angleradc=math.atan2(yc/xc)
angledegc=math.degrees(angleradc)

pid = PID(0.5,0.1,0.05,angledegc)


while True : 
    # PARTIE HAUTEUR 
    distanceh = lidar.read_distance()
    # print(f"La distance mesurée par le télémètre infrarouge est: {distance}cm")   
    vitesseh=pidh.compute(distanceh)
    mot_brushless.commande(vitesseh,0)
    # PARTIE XY 
    
    x=tag.localisation()[0]
    y=tag.localisation()[1]
    angle=tag.localisation()[3]
    
    dx=xc-x
    dy=yc-y
    anglerad=math.atan2(dy/dx)
    angledeg=math.degrees(anglerad)
    vitesse=pid.compute2(angledeg)
    mot_brushless.commande(vitesse,0)
    
    distance=math.sqrt(dx**2+dy**2)
    
    if abs(angledeg-angledegc) < 5 :
        vitesse2=pid.compute3(distance)
        mot_brushless.commande(vitesse2,0)
        
