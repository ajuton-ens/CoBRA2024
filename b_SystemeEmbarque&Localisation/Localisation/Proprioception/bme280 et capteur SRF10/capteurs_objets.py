# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 09:01:44 2024

@author: emili
"""
import smbus
import time
import numpy as np

bus = smbus.SMBus(1)

class capteurs():

    def __init__(self, addresse_SRF10 = 0x70, addresse_BNO055 = 0x28):
        self.address_SRF10 = addresse_SRF10
        self.address_BNO055 = addresse_BNO055
        data = bus.read_i2c_block_data(self.address_BNO055,0x3F,1)
        data[0]=0x20
        bus.write_byte_data(self.address_BNO055,0x07,1)
        bus.write_byte_data(self.address_BNO055,0x08,0x08)
        bus.write_byte_data(self.address_BNO055,0x0A,0x23)
        bus.write_byte_data(self.address_BNO055,0x0B,0x00)
        bus.write_byte_data(self.address_BNO055,0x09,0x1B)
        bus.write_byte_data(self.address_BNO055,0x07,0)
        bus.write_byte_data(self.address_BNO055,0x40,0x01)
        bus.write_byte_data(self.address_BNO055,0x3B,0x01)
        bus.write_byte_data(self.address_BNO055,0x3E,0x00)
        bus.write_byte_data(self.address_BNO055,0x3D,0x0C)
        print("fin de l'initialisation")
        pass
    
    def get(self):
        self.lancement_mesure_us()
        time.sleep(0.05)
        distance_us_cm = self.lecture_distance_us_cm()
        roll_brut = (bus.read_word_data(self.address_BNO055,0x1C))
        pitch_brut = (bus.read_word_data(self.address_BNO055,0x18))
        yaw_brut = (bus.read_word_data(self.address_BNO055,0x1A))
        roll = np.int16(roll_brut)/16
        pitch = np.int16(pitch_brut)/16
        yaw = np.int16(yaw_brut)/16
        return(distance_us_cm, roll, pitch, yaw)
    
    def lancement_mesure_us(self):
        bus.write_byte_data(self.address_SRF10, 0, 0x51)
        return -1

    def lecture_distance_us_cm(self):
        MSB = bus.read_byte_data(self.address_SRF10, 2)
        LSB = bus.read_byte_data(self.address_SRF10, 3)
        distance = (MSB << 8) + LSB
        return distance
