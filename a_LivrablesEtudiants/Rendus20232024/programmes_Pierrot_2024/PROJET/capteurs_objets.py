# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 09:01:44 2024

@author: emili
"""
import smbus
import time

bus = smbus.SMBus(1)
addresse_SRF10 = 0x70
class capteurs():
    
    def __init__(self, addresse_SRF10, addresse_BNO055):
        self.address_SRF10 = addresse_SRF10
        data = bus.read_i2c_block_data(ADDRESS,0x3F,1)
        data[0]=0x20
        bus.write_byte_data(ADDRESS,PAGE_SWAP,1)
        bus.write_byte_data(ADDRESS,ACC_CONF,0x08)
        bus.write_byte_data(ADDRESS,GYR_CONF_0,0x23)
        bus.write_byte_data(ADDRESS,GYR_CONF_1,0x00)
        bus.write_byte_data(ADDRESS,MAG_CONF,0x1B)
        bus.write_byte_data(ADDRESS,PAGE_SWAP,0)
        bus.write_byte_data(ADDRESS,TEMP_SOURCE,0x01)
        bus.write_byte_data(ADDRESS,UNIT_SEL,0x01)
        bus.write_byte_data(ADDRESS,PWR_MODE,0x00)
        bus.write_byte_data(ADDRESS,MODE_REG,FUSION_MODE)
        print("fin de l'initialisation")
        pass
    
    def get(self):
        lancement_mesure_us(0x51)
        time.sleep(0.5)
        distance_us_cm = lecture_distance_us_cm()
        roll = (bus.read_word_data(ADDRESS,0x1C))
        pitch = (bus.read_word_data(ADDRESS,0x18))
        yaw = (bus.read_word_data(ADDRESS,0x1A))
        return(distance_us_cm, roll, pitch, yaw)
    
    def lancement_mesure_us(self):
            bus.write_byte_data(self.address_SRF10, 0, 0x51)
            return -1

    def lecture_distance_us_cm(self):
            MSB = bus.read_byte_data(self.address_SRF10, 2)
            LSB = bus.read_byte_data(self.address_SRF10, 3)
            distance = (MSB << 8) + LSB
            return distance