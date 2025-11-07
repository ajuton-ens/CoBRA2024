import time

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
                        lsb = data[2*i]
                        msb = data[2*i+1]
                        value = (msb << 8) | lsb
                        if value > 32767:
                                value -= 65536
                        acc[axis] = value * 0.00981  # conversion mg → m/s²
                return acc




#Initialisation du module



# A envoyer lors du premier test





#while True :
#        data = i2cbus.read_byte_data(ADRESS_BNO055,CALIB_STAT)
#        print("CALIB_STAT : ", (data & 0xC0 >>6))
#        print("CALIB_STAT : ", (data & 0x30 >>4))
#        print("CALIB_STAT : ", (data & 0x0C >>2))
#        print("CALIB_STAT : ", (data & 0x03))
        
        
        