from moteurs_lib import *
import adafruit_bno055
import board
import time
import math
import sys
import smbus2

from BNO055_lib import *
from SRF10_lib import *
from control_lib import *


# Define motors

nb_channels = 16
address_HAT = 0x40

HAT = ServoKit(channels=nb_channels, address=address_HAT)
servo = Servo([270, 0, -10], [1840, 1107, 1000], HAT, 3)
main_motor = BrushlessMotor(HAT, 0)
back_motor = MCC(HAT, 2)


# Define sensors

i2c = smbus2.SMBus(1)
BNO_055_sensor = BNO055_i2c(i2c, 0x28) # Define BNO055 sensor
BNO_055_sensor.axis_remap=(1,2,0,1,1,1) # Remap axis
BNO_055_sensor.accel_range = ACCEL_2G # Change accelerometer range
BNO_055_sensor.mode = IMUPLUS_MODE # Change mode to obtain values

SRF10_sensor = SRF10_i2c(i2c, 0x70) # Define SFR10 sensor


# Define lists for angles and height

roll_q = [0]
roll_acc = [0]
roll_gyr = [0]
roll_eul = [0]

pitch_q = [0]
pitch_acc = [0]
pitch_gyr = [0]
pitch_eul = [0]

yaw_q = [0]
yaw_acc = [0]
yaw_gyr = [0]
yaw_eul = [0]


roll_filt = [0]
pitch_filt = [0]
yaw_filt = [0]

w_roll = [0]
w_pitch = [0]
w_yaw = [0]

heights = [0]



# Define data processing functions

def yaw_pitch_roll_from_q(q): 
    """Get the equivalent yaw-pitch-roll angles aka. intrinsic Tait-Bryan angles following the x-y-z convention"""

    qw = q[0]
    qx = q[1]
    qy = q[2]
    qz = q[3]


    roll = math.atan2(2.0*(qy*qz + qw*qx), qw*qw - qx*qx - qy*qy + qz*qz)*180/math.pi
    pitch = math.asin(-2.0*(qx*qz - qw*qy))*180/math.pi
    yaw = math.atan2(2.0*(qx*qy + qw*qz), qw*qw + qx*qx - qy*qy - qz*qz)*180/math.pi

    return roll, pitch, yaw  

def yaw_pitch_roll_from_acc(acc):
    """Get the equivalent yaw-pitch-roll angles aka. intrinsic Tait-Bryan angles following the x-y-z convention"""
    accx = acc[0]
    accy = acc[1]
    accz = acc[2]


    roll = math.atan2(accy/9.81, accz/9.81)*180/math.pi
    pitch = -math.atan2(accx/9.81, accz/9.81)*180/math.pi
    yaw = math.atan2(accx/9.81, accy/9.81)*180/math.pi

    return roll, pitch, yaw  

def yaw_pitch_roll_from_gyr(g, angles):
    """Get the equivalent yaw-pitch-roll angles aka. intrinsic Tait-Bryan angles following the x-y-z convention"""
    
    timediff = 0.150
    gyrx = g[0]
    gyry = g[1]
    gyrz = g[2]

    roll = angles[0]
    pitch = angles[1] 
    yaw = angles[2]

    roll = gyrx * timediff * 180/math.pi + roll
    pitch = gyry * timediff * 180/math.pi + pitch
    yaw = gyrz * timediff * 180/math.pi + yaw

    if roll < -180:
        roll = 180
    elif roll > 180:
        roll = -180

    if pitch < -180:
        pitch = 180
    elif pitch > 180:
        pitch = -180

    if yaw < -180:
        yaw = 180
    elif yaw > 180:
        yaw = -180


    return roll, pitch, yaw


def filter(angles_acc, angles_q, angles_gyr, angles_eul, trust_gyr, trust_acc, trust_eul):
    """Get the equivalent yaw-pitch-roll angles aka. intrinsic Tait-Bryan angles following the x-y-z convention"""

    roll_acc = angles_acc[0]
    pitch_acc = angles_acc[1] 
    yaw_acc = angles_acc[2]

    roll_gyr = angles_gyr[0]
    pitch_gyr = angles_gyr[1] 
    yaw_gyr = angles_gyr[2]

    roll_q = angles_q[0]
    pitch_q = angles_q[1] 
    yaw_q = angles_q[2]

    roll_eul = angles_q[0]
    pitch_eul = angles_q[1] 
    yaw_eul = angles_q[2]

    roll = trust_gyr * roll_gyr + (1-trust_gyr-trust_acc-trust_eul) * roll_q + trust_acc * roll_acc + trust_eul * roll_eul
    
    pitch = trust_gyr * pitch_gyr + (1-trust_gyr-trust_acc-trust_eul) * pitch_q + trust_acc * pitch_acc + trust_eul * pitch_eul
    
    yaw = trust_gyr * yaw_gyr + (1-trust_gyr-trust_eul) * yaw_q + trust_eul * yaw_eul

    return roll, pitch, yaw


def get_position():
    """Return position x,y of the blimp"""
    return (0,0)

# Evènements discrets

stateInit = True  # Initialisation 
stateA = False  # Tout droit
stateB = False  # Demi tour
stateC = False  # Arret


# Gestion du temps (discret)

time_init = time.time()
time_prec = time_init
time_current = time_init

time_arret = 10
time_demi_tour = 15


# Gestion de la boucle générale

while True :

    time_prec = time_current
    time_current = time.time() - time_init
    dt = time_current - time_prec



    try:

        if stateInit:       # Initialisation des variables 

            print('Début initialisation')

            # Initialisation angles
            roll_init = []
            pitch_init = []
            yaw_init = []

            for i in range(5):
                try:
                    q = BNO_055_sensor.quaternion
                    roll_init.append(yaw_pitch_roll_from_q(q)[0])
                    pitch_init.append(yaw_pitch_roll_from_q(q)[1])
                    yaw_init.append(yaw_pitch_roll_from_q(q)[2])
                except:
                    pass
                time.sleep(0.05)
            roll_initialisation = sum(roll_init)/len(roll_init)
            pitch_initialisation = sum(pitch_init)/len(pitch_init)
            yaw_initialisation = sum(yaw_init)/len(yaw_init) + 90

            height_init = SRF10_sensor.get_data()

            print('Initialisation roll : ', roll_initialisation)
            print('Initialisation pitch : ', pitch_initialisation)
            print('Initialisation yaw : ',yaw_initialisation)
            print('Initialisation height : ',height_init)

            # Initialisation PIDs
            PID_height = PID(-1/20,0,0,height_init)
            PID_yaw = PID(1/80,0,0,360-yaw_initialisation)
            PID_w_yaw = PID(1/45,0,0,0)

            # Initialisation moteur
            main_motor.initialisation()
            back_motor.initialisation()
            time.sleep(2.5)

            # Initialisation position
            x0 = 0
            y0 = 0

            print('Fin initialisation')

            stateInit = False
            stateA = True
            
            back_motor.stop()
            main_motor.set_speed(0)
            servo.set_angle(0)

        try:   # Get values from sensors 

            q = BNO_055_sensor.quaternion       # Angle from quaternion
            rpy_q = yaw_pitch_roll_from_q(q)

            acc = BNO_055_sensor.gravity        # Angle from gravity sensor
            rpy_acc = yaw_pitch_roll_from_acc(acc)

            gyr = BNO_055_sensor.gyro           # Angle from gyro sensor
            rpy_gyr = yaw_pitch_roll_from_gyr(gyr, (roll_gyr[-1], pitch_gyr[-1], yaw_gyr[-1]))

            rpy_eul = BNO_055_sensor.euler      # Angle from euler

            g = BNO_055_sensor.gyro             # Angular speed from gyro

            height = SRF10_sensor.get_data()  # Get height

            x,y = get_position()        # Current position

            # Add values in the lists
            heights.append(height)

            roll_q.append(rpy_q[0]) 
            roll_acc.append(rpy_acc[0])
            roll_gyr.append(rpy_gyr[0])

            pitch_q.append(rpy_q[1]) 
            pitch_acc.append(rpy_acc[1]) 
            pitch_gyr.append(rpy_gyr[1]) 

            yaw_q.append(rpy_q[2]) 
            yaw_acc.append(rpy_acc[2]) 
            yaw_gyr.append(rpy_gyr[2]) 

            w_roll.append(g[0]*180/3.1415)
            w_pitch.append(g[1]*180/3.1415)
            w_yaw.append(g[2]*180/3.1415)



            angles_filt = filter(rpy_acc,rpy_q, rpy_gyr, rpy_eul, 0, 0.2, 0.3)
            roll_filt.append(angles_filt[0] - roll_initialisation)
            pitch_filt.append(angles_filt[1] - pitch_initialisation)
            yaw_filt.append((angles_filt[2] - yaw_initialisation+360)%360)

            # print raw angles : 

            # print(yaw_q[-1])
            # print(yaw_gyr[-1])
            # print(rpy_eul[2])
            # print(angles_filt)
            # print("yaw : ", yaw_filt[-1])
            # print("time : ", time_current)
            # print()

        except :
            pass
      

        if stateA:
            """ Avance tout droit """


            # Calcul les écarts pour l'asservissement
            ecart_height = PID_height.update(heights[-1])
            ecart_yaw = PID_yaw.update(yaw_filt[-1])
            ecart_w_yaw = PID_w_yaw.update(w_yaw[-1])

            # Moteurs
            main_motor.set_speed(0.4)
            back_motor.set_speed(-(ecart_yaw + ecart_w_yaw) + 0.05)
            servo.set_angle(180 + ecart_height)


            # print values

            # print("yaw : ", yaw_filt[-1])
            # print("heut : ", heights[-1])
            # print("yaw init : ", yaw_initialisation)
            # print("ecart yaw : ", ecart_yaw)
            # print("ecart vit yaw : ", ecart_w_yaw)
            # print("ecart hauteur : ", ecart_height)
            # print("Commande moteur : ", -(ecart_yaw + ecart_w_yaw))
            # print()
            # print(ecart_height)
            # print(heights[-1])
            # print()


            # Change d'état
            demi_tour = time_current > time_demi_tour and time_current < time_demi_tour+1 and False
            arret = time_current > time_arret and time_current < time_arret + 1 and False


            if demi_tour:  # Réinitialise les valeurs booléennes
                print("Demi tour !")
                stateA = False
                stateB = True
                stateC = False
                demi_tour = False

            elif arret:  # Réinitialise les valeurs booléennes
                print("Arret !")
                stateA = False
                stateB = False
                stateC = True
                arret = False


        if stateB:
            """ Demi tour """

            # Moteurs
            back_motor.set_speed(0.3)
            main_motor.set_speed(0)

            # Arrête le moteur arrière et change la consigne            
            if yaw_filt[-1] < 160 :
                PID_yaw = PID(1/80,0,0,90)
                stateA = True
                stateB = False
                back_motor.set_speed(0)
                print("Arret demi tour ! ")

        if stateC:
            """ Arret """

            # Calcul les écarts pour les asservissements
            ecart_yaw = PID_yaw.update(yaw_filt[-1])
            ecart_w_yaw = PID_w_yaw.update(w_yaw[-1])

            # Moteurs
            back_motor.set_speed(-(ecart_yaw + ecart_w_yaw) + 0.05)
            main_motor.set_speed(0.4)
            servo.set_angle(20)

            # On arrête tout
            if time_current > time_arret + 6:
                main_motor.set_speed(0)
                servo.set_angle(0)
                break



        time.sleep(0.5)



    except KeyboardInterrupt:
        print(" ")
        print("Shutdown requested... exiting")
        back_motor.stop()
        main_motor.set_speed(0)
        servo.set_angle(0)
        sys.exit(0)

