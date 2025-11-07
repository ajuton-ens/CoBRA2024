import cv2
from picamera2 import Picamera2
import time
from pyapriltags import Detector
import numpy as np
import smbus2
from math import*
import matplotlib.pyplot as plt
import socket
import json

PAGE_SWAP=0x07
ACC_CONF= 0x08
GYR_CONF_0=0x0A
GYR_CONF_1=0x0B
MAG_CONF=0x09
TEMP_SOURCE=0x40
UNIT_SEL=0x3B
PWR_MODE=0x3E
ADRESS_BNO055=0x28 #adresse 7 bits du BONO055
HEADING=0x1A
MODE_REG=0x3D
FUSION_MODE=0x0C
UNIQUE_ID=0x50
CALIB_STAT = 0x35
MAG_DATA_Z_MSB =0x12
MAG_DATA_Z_LSB=0x13

CHIP_ID = 0x00
ACC_ID = 0x01
MAG_ID = 0x02
GYR_ID = 0x03
SW_REV_ID_LSB = 0x04
SW_REV_ID_MSB = 0x05
BL_REV_ID = 0x06
PAGE_ID = 0x07

ACC_DATA_X_LSB = 0x08
ACC_DATA_X_MSB = 0x09
MAG_DATA_X_LSB = 0x0E
MAG_DATA_X_MSB = 0x0F
MAG_DATA_Y_LSB = 0x10
MAG_DATA_Y_MSB = 0x11
MAG_DATA_Z_LSB = 0x12
MAG_DATA_Z_MSB = 0x13

GYR_DATA_X_LSB = 0x14
GYR_DATA_X_MSB = 0x15
GYR_DATA_Y_LSB = 0x16
GYR_DATA_Y_MSB = 0x17
GYR_DATA_Z_LSB = 0x18
GYR_DATA_Z_MSB = 0x19

EUL_HEADING_LSB = 0x1A
EUL_HEADING_MSB = 0x1B
EUL_ROLL_LSB = 0x1C
EUL_ROLL_MSB = 0x1D
EUL_PITCH_LSB = 0x1E
EUL_PITCH_MSB = 0x1F

QUA_DATA_W_LSB = 0x20
QUA_DATA_W_MSB = 0x21
QUA_DATA_X_LSB = 0x22
QUA_DATA_X_MSB = 0x23
QUA_DATA_Y_LSB = 0x24
QUA_DATA_Y_MSB = 0x25
QUA_DATA_Z_LSB = 0x26
QUA_DATA_Z_MSB = 0x27

LIA_DATA_X_LSB = 0x28
LIA_DATA_X_MSB = 0x29
LIA_DATA_Y_LSB = 0x2A
LIA_DATA_Y_MSB = 0x2B
LIA_DATA_Z_LSB = 0x2C
LIA_DATA_Z_MSB = 0x2D

GRV_DATA_X_LSB = 0x2E
GRV_DATA_X_MSB = 0x2F
GRV_DATA_Y_LSB = 0x30
GRV_DATA_Y_MSB = 0x31
GRV_DATA_Z_LSB = 0x32
GRV_DATA_Z_MSB = 0x33

TEMP = 0x34
CALIB_STAT = 0x35
SELFTEST_RESULT = 0x36
INT_STA = 0x37
SYS_CLK_STATUS = 0x38
SYS_STATUS = 0x39
SYS_ERR = 0x3A
UNIT_SEL = 0x3B
OPR_MODE = 0x3D
PWR_MODE = 0x3E
SYS_TRIGGER = 0x3F
TEMP_SOURCE = 0x40
AXIS_MAP_CONFIG = 0x41
AXIS_MAP_SIGN = 0x42

# SIC MATRIX 0 - 8
SIC_MATRIX_LSB0 = 0x43
SIC_MATRIX_MSB0 = 0x44
SIC_MATRIX_LSB1 = 0x45
SIC_MATRIX_MSB1 = 0x46
SIC_MATRIX_LSB2 = 0x47
SIC_MATRIX_MSB2 = 0x48
SIC_MATRIX_LSB3 = 0x49
SIC_MATRIX_MSB3 = 0x4A
SIC_MATRIX_LSB4 = 0x4B
SIC_MATRIX_MSB4 = 0x4C
SIC_MATRIX_LSB5 = 0x4D
SIC_MATRIX_MSB5 = 0x4E
SIC_MATRIX_LSB6 = 0x4F
SIC_MATRIX_MSB6 = 0x50
SIC_MATRIX_LSB7 = 0x51
SIC_MATRIX_MSB7 = 0x52
SIC_MATRIX_LSB8 = 0x53
SIC_MATRIX_MSB8 = 0x54

# ACC OFFSET
ACC_OFFSET_X_LSB = 0x55
ACC_OFFSET_X_MSB = 0x56
ACC_OFFSET_Y_LSB = 0x57
ACC_OFFSET_Y_MSB = 0x58
ACC_OFFSET_Z_LSB = 0x59
ACC_OFFSET_Z_MSB = 0x5A

# MAG OFFSET
MAG_OFFSET_X_LSB = 0x5B
MAG_OFFSET_X_MSB = 0x5C
MAG_OFFSET_Y_LSB = 0x5D
MAG_OFFSET_Y_MSB = 0x5E
MAG_OFFSET_Z_LSB = 0x5F
MAG_OFFSET_Z_MSB = 0x60

# GYR OFFSET
GYR_OFFSET_X_LSB = 0x61
GYR_OFFSET_X_MSB = 0x62
GYR_OFFSET_Y_LSB = 0x63
GYR_OFFSET_Y_MSB = 0x64
GYR_OFFSET_Z_LSB = 0x65
GYR_OFFSET_Z_MSB = 0x66

# RADIUS
ACC_RADIUS_LSB = 0x67
ACC_RADIUS_MSB = 0x68
MAG_RADIUS_LSB = 0x69
MAG_RADIUS_MSB = 0x6A

ACC_CONF = 0x08
MAG_CONF = 0x09
GYR_CONF_0 = 0x0A
GYR_CONF_1 = 0x0B
ACC_SLEEP_CONF = 0x0C
GYR_SLEEP_CONF = 0x0D
INT_MSK = 0x0F
INT_EN = 0x10
ACC_AM_THRES = 0x11
ACC_INT_SETTINGS = 0x12
ACC_HG_DURATION = 0x13
ACC_HG_THRES = 0x14
ACC_NM_THRES = 0x15
ACC_NM_SET = 0x16
GYR_INT_SETTING = 0x17
GYR_HR_X_SET = 0x18
GYR_DUR_X = 0x19
GYR_HR_Y_SET = 0x1A
GYR_DUR_Y = 0x1B
GYR_HR_Z_SET = 0x1C
GYR_DUR_Z = 0x1D
GYR_AM_THRES = 0x1E
GYR_AM_SET = 0x1F

# UNIQUE_ID (16 octets)
UNIQUE_ID_START = 0x50
UNIQUE_ID_END = 0x5F









#Initialisation du module



# A envoyer lors du premier test





#while True :
#        data = i2cbus.read_byte_data(ADRESS_BNO055,CALIB_STAT)
#        print("CALIB_STAT : ", (data & 0xC0 >>6))
#        print("CALIB_STAT : ", (data & 0x30 >>4))
#        print("CALIB_STAT : ", (data & 0x0C >>2))
#        print("CALIB_STAT : ", (data & 0x03))
        
        
        

class BNO055():
        """ Biliothèque pour l'utilisation de la centrale supelec inertielle BNO055"""
        def __init__(self, bus,i2c_address=ADRESS_BNO055):
                self.address = i2c_address
                self.bus = bus
                self.bus.write_byte_data(ADRESS_BNO055,PAGE_SWAP,1)
                data = self.bus.read_byte_data(ADRESS_BNO055,UNIQUE_ID)
                print("UNIQUE_ID du BNO055 : ",data)
                self.bus.write_byte_data(ADRESS_BNO055,PAGE_SWAP,0)
                data = self.bus.read_byte_data(ADRESS_BNO055,CALIB_STAT)
                #Config en mode fusion
                self.bus.write_byte_data(ADRESS_BNO055,ACC_CONF,0x08)
                self.bus.write_byte_data(ADRESS_BNO055,GYR_CONF_0,0x23)
                self.bus.write_byte_data(ADRESS_BNO055,GYR_CONF_1,0x00)
                self.bus.write_byte_data(ADRESS_BNO055,MAG_CONF,0x1B)
                self.bus.write_byte_data(ADRESS_BNO055,PAGE_SWAP,0)
                self.bus.write_byte_data(ADRESS_BNO055,TEMP_SOURCE,0x01)
                self.bus.write_byte_data(ADRESS_BNO055,UNIT_SEL,0x01)
                self.bus.write_byte_data(ADRESS_BNO055,PWR_MODE,0x00)
                self.bus.write_byte_data(ADRESS_BNO055,MODE_REG,FUSION_MODE)

        #        
        def calibration(self):
                
                print("Faire des 8 avec le capteur")
                n=0
                t0=time.time()
                while True :
                        time.sleep(0.1)
                        t1 = time.time()
                        data = self.bus.read_byte_data(ADRESS_BNO055,CALIB_STAT)
                        
                        if (data & 0xC0 >>6)==3 and  (data & 0xC0 >>6)==3 and (data & 0xC0 >>6)==3 and  (data & 0xC0 >>6)==3 :
                                print("Calibration réussie")
                                break
                        if (t1-t0)>5:
                                print("Erreur de calibration")
                                break
        

        def read_euler(self):
                while True:
                        registres_lus = self.bus.read_i2c_block_data(ADRESS_BNO055,EUL_HEADING_LSB,6) 
                        
                        
                        data={}
                        data1 = registres_lus[EUL_PITCH_LSB-EUL_HEADING_LSB]
                        data2 = registres_lus[EUL_PITCH_MSB-EUL_HEADING_LSB]
                        data3=int(data2<<8)+data1
                        if data3 > 32767 :
                                data3 = data3 - 65536
                        data["pitch"]= float(data3)/16
                        #print(data1,data2,data["pitch"])
                        data1 = registres_lus[EUL_ROLL_LSB-EUL_HEADING_LSB]
                        data2 = registres_lus[EUL_ROLL_MSB-EUL_HEADING_LSB]
                        data3=int(data2<<8)+data1
                        if data3 > 32767 :
                                data3 = data3 - 65536
                        data["roll"]= float(data3)/16
                        #print(data1,data2,data["roll"])
                        data1 = registres_lus[EUL_HEADING_LSB-EUL_HEADING_LSB]
                        data2 = registres_lus[EUL_HEADING_MSB-EUL_HEADING_LSB]
                        data3=int(data2<<8)+data1
                        if data3 > 32767 :
                                data3 = data3 - 65536
                        data["heading"]= float(data3)/16
                
                        #print(data1,data2,data["heading"])
                        return data
        def read_acceleration(self):
                data = self.bus.read_i2c_block_data(self.address, ACC_DATA_X_LSB, 6)
                acc = {}
                for i, axis in enumerate(['x', 'y', 'z']):
                        lsb = data[2*i]
                        msb = data[2*i + 1]
                        value = (msb << 8) | lsb
                        if value > 32767:
                                value -= 65536

                        acc[axis] = value * 0.00981  # à adapter si autre échelle
                return acc
        def read_linear_acceleration(self):
                data = self.bus.read_i2c_block_data(self.address, 0x28, 6)
                acc = {}
                for i, axis in enumerate(['x', 'y', 'z']):
                        lsb = data[2 * i]
                        msb = data[2 * i + 1]
                        value = (msb << 8) | lsb
                        if value > 32767:
                                value -= 65536
                        acc[axis] = value * 0.00981  # conversion mg → m/s²
                return acc


                        

i2cbus = smbus2.SMBus(1) 
mybno = BNO055(i2cbus)
mybno.calibration()










picam2 = Picamera2()
WIDTH,HEIGH=1536,864
picam2.configure(picam2.create_preview_configuration({'size':(WIDTH,HEIGH)}))
picam2.start()

at_detector = Detector(families="tag36h11",nthreads=1,quad_sigma=0.0,refine_edges=1,\
decode_sharpening=0.25,debug=0)

#coefficients de distorsion de la camera


mtx = np.array([[ 977.08159964 	,  0.00000000e+00,  789.18761132],[ 0.00000000e+00,  977.14004212, 434.47165678],[ 0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])
dist = np.array([[-0.02727091,  0.1312434,   0.00479796,  0.00269239, -1.30723302]])

fx = mtx[0][0]
cx = mtx[0][2]
fy = mtx[1][1]
cy = mtx[1][2]


#Positions des tags dans l'environnement
listePoints3D = listePoints3D = {100: (0.085, 0.27, 0), 101: (0.085, 1.27, 0), 102: (0.085, 2.27, 0), 103: (0.085, 3.27, 0), 104: (0.085, 4.27, 0), 105: (0.085, 5.27, 0), 106: (0.085, 6.27, 0), 107: (0.085, 7.27, 0), 108: (0.085, 8.27, 0), 109: (0.085, 9.27, 0), 110: (1.085, 0.27, 0), 111: (1.085, 1.27, 0), 112: (1.085, 2.27, 0), 113: (1.085, 3.27, 0), 114: (1.085, 4.27, 0), 115: (1.085, 5.27, 0), 116: (1.085, 6.27, 0), 117: (1.085, 7.27, 0), 118: (1.085, 8.27, 0), 119: (1.085, 9.27, 0), 120: (2.085, 0.27, 0), 121: (2.085, 1.27, 0), 122: (2.085, 2.27, 0), 123: (2.085, 3.27, 0), 124: (2.085, 4.27, 0), 125: (2.085, 5.27, 0), 126: (2.085, 6.27, 0), 127: (2.085, 7.27, 0), 128: (2.085, 8.27, 0), 129: (2.085, 9.27, 0), 130: (3.085, 0.27, 0), 131: (3.085, 1.27, 0), 132: (3.085, 2.27, 0), 133: (3.085, 3.27, 0), 134: (3.085, 4.27, 0), 135: (3.085, 5.27, 0), 136: (3.085, 6.27, 0), 137: (3.085, 7.27, 0), 138: (3.085, 8.27, 0), 139: (3.085, 9.27, 0), 140: (4.085, 0.27, 0), 141: (4.085, 1.27, 0), 142: (4.085, 2.27, 0), 143: (4.085, 3.27, 0), 144: (4.085, 4.27, 0), 145: (4.085, 5.27, 0), 146: (4.085, 6.27, 0), 147: (4.085, 7.27, 0), 148: (4.085, 8.27, 0), 149: (4.085, 9.27, 0), 150: (5.085, 0.27, 0), 151: (5.085, 1.27, 0), 152: (5.085, 2.27, 0), 153: (5.085, 3.27, 0), 154: (5.085, 4.27, 0), 155: (5.085, 5.27, 0), 156: (5.085, 6.27, 0), 157: (5.085, 7.27, 0), 158: (5.085, 8.27, 0), 159: (5.085, 9.27, 0), 160: (6.085, 0.27, 0), 161: (6.085, 1.27, 0), 162: (6.085, 2.27, 0), 163: (6.085, 3.27, 0), 164: (6.085, 4.27, 0), 165: (6.085, 5.27, 0), 166: (6.085, 6.27, 0), 167: (6.085, 7.27, 0), 168: (6.085, 8.27, 0), 169: (6.085, 9.27, 0), 170: (7.085, 0.27, 0), 171: (7.085, 1.27, 0), 172: (7.085, 2.27, 0), 173: (7.085, 3.27, 0), 174: (7.085, 4.27, 0), 175: (7.085, 5.27, 0), 176: (7.085, 6.27, 0), 177: (7.085, 7.27, 0), 178: (7.085, 8.27, 0), 179: (7.085, 9.27, 0), 180: (8.085, 0.27, 0), 181: (8.085, 1.27, 0), 182: (8.085, 2.27, 0), 183: (8.085, 3.27, 0), 184: (8.085, 4.27, 0), 185: (8.085, 5.27, 0), 186: (8.085, 6.27, 0), 187: (8.085, 7.27, 0), 188: (8.085, 8.27, 0), 189: (8.085, 9.27, 0), 190: (9.085, 0.27, 0), 191: (9.085, 1.27, 0), 192: (9.085, 2.27, 0), 193: (9.085, 3.27, 0), 194: (9.085, 4.27, 0), 195: (9.085, 5.27, 0), 196: (9.085, 6.27, 0), 197: (9.085, 7.27, 0), 198: (9.085, 8.27, 0), 199: (9.085, 9.27, 0)}

def capture():
    img=cv2.cvtColor(picam2.capture_array(),cv2.COLOR_BGR2GRAY) #prise d'une photo puis correction
    img_undistorded = cv2.undistort(img, mtx, dist, None, newCameraMatrix=mtx)
    #indication de la taille des tags, lancement de la detection
    tags=at_detector.detect(img_undistorded,estimate_tag_pose=True,camera_params=[fx,fy,cx,cy],tag_size=0.173) 
    return tags

def calculAngles(R):
    sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
    singular = sy < 1e-6
    if not singular:
        x = np.arctan2(R[2, 1], R[2, 2])
        y = np.arctan2(-R[2, 0], sy)
        z = np.arctan2(R[1, 0], R[0, 0])
    else:
        x = np.arctan2(-R[1, 2], R[1, 1])
        y = np.arctan2(-R[2, 0], sy)
        z = 0
    return np.degrees(np.array([x, y, z]))


matrice=np.array([[-1,0,0],[0,1,0],[0,0,1]])
# while True:
#     tags=capture()
#     positions=[]
#     positionMoyenne=np.array([0,0,0],dtype='float64')
#     angles=[]
#     angleMoyen=np.array([0,0,0],dtype='float64')
#     for tag in tags:

#         #calcul des angles suivant Xw, Yw et Zw
#         angles.append(np.array(calculAngles(tag.pose_R)))
        
#         pose=np.dot(np.transpose(tag.pose_R),tag.pose_t)
#         #formule pour trouver la position  partir du resultat apriltag
#         try :
#            positions.append(np.dot(matrice,np.transpose(pose)[0])+np.array(listePoints3D[tag.tag_id])) 
#         except : 
#            print("tag inconnu detecte : ",tag.tag_id)
         
#     #Calcul de la moyenne des différentes positions mesurées
#     for position in positions:
#         positionMoyenne+=position
#     for angle in angles:
#         angleMoyen+=angle
#     n=len(positions)
#     time.sleep(1)
#     print("fonctionnement")
#     if n!=0:
#         positionMoyenne=positionMoyenne/n
#         print("position et nb tags : ", positionMoyenne,n)
#         angleMoyen=angleMoyen/n
#         print("angle : ", angleMoyen)

angle_fusionne = np.array([0.0, 0.0, 0.0])





# while True:
#     tags = capture()
#     angleMoyen = np.array([0, 0, 0], dtype='float64')
#     n = 0
#     print("nb tags: ", len(tags))
#     for tag in tags:
#         angleMoyen += np.array(calculAngles(tag.pose_R))
#         n += 1

#     if n > 0:
#         angleMoyen /= n
#         alpha=(1-exp(-n))
#     else:
#           alpha=0
#     angle_euler = mybno.read_euler()
#     angle_bno = np.array([angle_euler["pitch"], angle_euler["roll"], angle_euler["heading"]])

#     angle_fusionne = (1-alpha) * angle_bno + alpha * angleMoyen

#     print("Angle caméra:", angleMoyen)
#     print("Angle BNO055:", angle_bno)
#     print("Angle fusionné:", angle_fusionne)

#     time.sleep(0.1)
    



adresse_socket = ("",8087)
socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.bind(adresse_socket)
socket_server.listen(1)

print("En attente de connexion du client...")
socket_cree_pour_client, adresse_client = socket_server.accept()
print(f"Client connecté depuis {adresse_client}")

while True:
    try:
        a_json = json.dumps(mybno.read_linear_acceleration())
        socket_cree_pour_client.send(a_json.encode("utf-8"))
    except:
        break
    time.sleep(0.3)

print("Fin de la communication")
socket_cree_pour_client.close()
socket_server.close()



