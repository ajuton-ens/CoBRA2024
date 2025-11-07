import time
import smbus
import numpy as np
import csv


PAGE_SWAP=0x07
ACC_CONF= 0x08
GYR_CONF_0=0x0A
GYR_CONF_1=0x0B
MAG_CONF=0x09
TEMP_SOURCE=0x40
UNIT_SEL=0x3B
PWR_MODE=0x3E
ADDRESS=0x28 #adresse 7 bits du BNO055
HEADING=0x1A
MODE_REG=0x3D
FUSION_MODE=0x0C

#Initialisation du module
i2cbus = smbus.SMBus(1)
time.sleep(0.5)
data = i2cbus.read_i2c_block_data(ADDRESS,0x3F,1)
print(data[0])
data[0]=0x20
time.sleep(0.5)
# i2cbus.write_byte_data(ADDRESS,0x3F,32)

with open("mesures_angles.csv","w") as mesures:
            writer = csv.writer(mesures, delimiter = ';')
            writer.writerow(['temps', 'pitch_deg', 'yaw_deg', 'roll_deg'])

# A envoyer lors du premier test
i2cbus.write_byte_data(ADDRESS,PAGE_SWAP,1)
i2cbus.write_byte_data(ADDRESS,ACC_CONF,0x08)
i2cbus.write_byte_data(ADDRESS,GYR_CONF_0,0x23)
i2cbus.write_byte_data(ADDRESS,GYR_CONF_1,0x00)
i2cbus.write_byte_data(ADDRESS,MAG_CONF,0x1B)
i2cbus.write_byte_data(ADDRESS,PAGE_SWAP,0)
i2cbus.write_byte_data(ADDRESS,TEMP_SOURCE,0x01)
i2cbus.write_byte_data(ADDRESS,UNIT_SEL,0x01)
i2cbus.write_byte_data(ADDRESS,PWR_MODE,0x00)
i2cbus.write_byte_data(ADDRESS,MODE_REG,FUSION_MODE)
temps_0 = time.time()
while True :
    try :
        roll = (i2cbus.read_word_data(ADDRESS,0x1E))
        pitch = (i2cbus.read_word_data(ADDRESS,0x1C))
        yaw = (i2cbus.read_word_data(ADDRESS,0x1A))
        #time.sleep(0.5)
        temp = i2cbus.read_byte_data(ADDRESS,0x34)
        #time.sleep(0.5)
        orientation = (i2cbus.read_word_data(ADDRESS,0x12))
        roll_deg = np.int16(roll)/16
        pitch_deg = np.int16(pitch)/16
        yaw_deg = np.int16(yaw)/16
        temps = time.time()-temps_0
        #print("temps = "+str(temps)+"  pitch : "+str( pitch_deg)+"  yaw :"+str( yaw_deg )+"  roll : "+str( roll_deg)+"  temp : "+str(temp) + " orientation : " + str(np.int16(orientation)))
        with open("mesures_angles.csv","a") as mesures:
            writer = csv.writer(mesures, delimiter = ';')
            writer.writerow([temps, pitch_deg, yaw_deg, roll_deg])
        #time.sleep(1)
    except :
        break
