from marvelmind import MarvelmindHedge
import sys
# from acquisitionPos import Acq_position
import threading
from moteurs_lib import *
import adafruit_bno055
import board
import time
import math
import smbus2
from BNO055_lib import *
from control_lib import *


#init
position = (0.0,0.0)
mutex_lire = False
mutex_ecrire = False

liste_points=[(1,1),(3,2),(3,3)]  #liste des points à explorer
critere = .5 #Critere pour considérer que le dirigeable est assez proche d'un point pour y être passé


def Acq_position():
    global position
    global mutex_lire
    global mutex_ecrire    
    hedge = MarvelmindHedge(tty="/dev/ttyACM0", adr=None, debug=False)  # create MarvelmindHedge thread
    
    if len(sys.argv) > 1:
        hedge.tty = sys.argv[1]
    
    hedge.start()  # start thread
    while True:
        time.sleep(0.01)
        try:
            hedge.dataEvent.wait(1)
            hedge.dataEvent.clear()
            if hedge.positionUpdated:
                position_tempo = hedge.position()
                while mutex_lire == True:
                    time.sleep(0.001)
                mutex_ecrire = True
                position = position_tempo
                mutex_ecrire = False
                
        except KeyboardInterrupt:
            hedge.stop()  # stop and close serial port


def affichPos():
    global position
    global mutex_ecrire
    global mutex_lire
    global positionAff
    positionAff = (0.0,0.0)
    while True:
        time.sleep(1)
        while mutex_ecrire == True:
            time.sleep(0.001)
        mutex_lire = True
        positionAff = (position[1], position[2])
        mutex_lire = False
        print(positionAff)
        
threadAff = threading.Thread(target=affichPos)
threadAcq = threading.Thread(target=Acq_position)

threadAff.start()
threadAcq.start()


# Define motors
nb_channels = 16
address_HAT = 0x40

HAT = ServoKit(channels=nb_channels, address=address_HAT)
servo = Servo([270, 0, -10], [1840, 1107, 1000], HAT, 3)
main_motor = BrushlessMotor(HAT, 0)
back_motor = MCC(HAT, 2)


# Define sensor
i2c = smbus2.SMBus(1)
sensor = BNO055_i2c(i2c, 0x28)
sensor.axis_remap=(1,2,0,1,1,1)
sensor.accel_range = ACCEL_2G
sensor.mode = IMUPLUS_MODE


last_val = 0xFFFF


# Define lists for angles
x = [0]

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



# Initialisation motor
print('Début initialisation')

roll_init = []
pitch_init = []
yaw_init = []
main_motor.initialisation()
back_motor.initialisation()
time.sleep(2.5)
for i in range(10):
    try:
        q = sensor.quaternion
        roll_init.append(yaw_pitch_roll_from_q(q)[0])
        pitch_init.append(yaw_pitch_roll_from_q(q)[1])
        yaw_init.append(yaw_pitch_roll_from_q(q)[2])
    except:
        pass
    time.sleep(0.05)
roll_initialisation = sum(roll_init)/len(roll_init)
pitch_initialisation = sum(pitch_init)/len(pitch_init)
yaw_initialisation = sum(yaw_init)/len(yaw_init)

print('Initialisation roll : ', roll_initialisation)
print('Initialisation pitch : ', pitch_initialisation)
print('Initialisation yaw : ',yaw_initialisation)


print('Fin initialisation')


# Initialisation PIDs
PID_pitch = PID(1,1,0,0)
PID_yaw = PID(1/80,0,0,0)
PID_w_yaw = PID(1/45,0,0,0)

stateA = True
stateA_A = True
stateA_B = False
stateA_C = False


pitch_offset = 13
yaw_offset = 0

time_init = time.time()
time_prec = time_init
time_current = time_init

while len(liste_points)!=0 :
    time_prec = time_current
    time_current = time.time() - time_init
    dt = time_current - time_prec
    PID_yaw = PID(1/80,0,1/200,math.atan((liste_points[0][0] - positionAff[0])/(liste_points[0][1] - positionAff[1])))

    try :
        time.sleep(0.1)
    except KeyboardInterrupt:
        threadAff.join()
        threadAcq.join()
        break
    try:
        try:
            q = sensor.quaternion
            rpy_q = yaw_pitch_roll_from_q(q)

            acc = sensor.gravity
            rpy_acc = yaw_pitch_roll_from_acc(acc)

            gyr = sensor.gyro
            rpy_gyr = yaw_pitch_roll_from_gyr(gyr, (roll_gyr[-1], pitch_gyr[-1], yaw_gyr[-1]))

            rpy_eul = sensor.euler

            g = sensor.gyro

        except :
            pass

        

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

        # print(yaw_q[-1])
        # print(yaw_gyr[-1])
        # print(rpy_eul[2])
        # print("")


        angles_filt = filter(rpy_acc,rpy_q, rpy_gyr, rpy_eul, 0, 0.2, 0.3)
        # print(angles_filt)
        roll_filt.append(angles_filt[0] - roll_initialisation)
        pitch_filt.append(angles_filt[1] - pitch_initialisation)
        yaw_filt.append(angles_filt[2] - yaw_initialisation)

        main_motor.set_speed(0.2)
        k = 1

        ecart_pitch = PID_pitch.update(pitch_filt[-1])

        servo.set_angle(160 + k * ecart_pitch)

        # Asservissement yaw
        ecart_yaw = PID_yaw.update(yaw_filt[-1])
        ecart_w_yaw = PID_w_yaw.update(w_yaw[-1])

        #print("yaw : ", yaw_filt[-1])
        # print("yaw init : ", yaw_initialisation)
        #print("ecart yaw : ", ecart_yaw)
        # print("ecart vit yaw : ", ecart_w_yaw)
        print("Commande moteur : ", -(ecart_yaw + ecart_w_yaw))
        # print("")
        commande_moteur=-(ecart_yaw + ecart_w_yaw)
        if commande_moteur**2>0.25**2:
            commande_moteur=0.25

        back_motor.set_speed(commande_moteur + 0.05)

        
        if ((positionAff[0]-liste_points[0][0])**2 +(positionAff[1]-liste_points[0][1])**2)<=critere**2:
            liste_points.remove(liste_points[0])
            print("points atteint")
        time.sleep(0.5)



    except KeyboardInterrupt:
        print(" ")
        print("Shutdown requested... exiting")
        back_motor.stop()
        main_motor.set_speed(0)
        servo.set_angle(0)
        sys.exit(0)
