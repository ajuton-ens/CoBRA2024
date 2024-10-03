# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 10:02:13 2024

@author: emili
"""

import smbus
import time
bus = smbus.SMBus(1)
address = 0x70

#REQUIRES 5V
def lancement_mesure_us():
        bus.write_byte_data(0x70, 0, 0x51)
        return -1

def lecture_distance_us_cm():
        MSB = bus.read_byte_data(0x70, 2)
        LSB = bus.read_byte_data(0x70, 3)
        distance = (MSB << 8) + LSB
        return distance
    
while True:
        lancement_mesure_us(0x51)
        time.sleep(0.5)