#-*- coding: utf-8 -*-
"""
Created on Fri Mar 29 12:02:39 2024

@author: emili
"""

import smbus2
import time
import numpy as np
from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)
import warnings
import RPi.GPIO as GPIO

bus = smbus2.SMBus(1)

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
        time.sleep(0.01)
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
    
class actionneur:
    def __init__(self, type, pin):
        self.type = None
        self.pin = pin

    def pulse_width_to_thr(self, pw):
        return (pw - 1445)/(2170 - 1445)

    def set_pulse_width(self, pw):
        thr = self.pulse_width_to_thr(pw)
        kit.continuous_servo[self.pin].throttle = thr

class servo(actionneur):
    def __init__(self, caract, pin):
        super().__init__("servo", pin)
        self.pin = pin
        self.caract = caract

    def commande_angle(self, angle):
        pw = 0
        if angle > self.caract[1][0]:
            pw = self.caract[0][0]
            warnings.warn("Angle trop important !")
        elif angle <= self.caract[1][0] and angle > self.caract[1][1]:
            pw = (angle-self.caract[1][1])/(self.caract[1][0]-self.caract[1][1])*(self.caract[0][0]-self.caract[0][1]) + self.caract[0][1]
        elif angle <= self.caract[1][1] and angle >= self.caract[1][2]:
            pw = (angle-self.caract[1][2])/(self.caract[1][1]-self.caract[1][2])*(self.caract[0][1]-self.caract[0][2]) + self.caract[0][2]
        else :
            pw = self.caract[0][1]
            warnings.warn("Angle trop faible !")
        
        self.set_pulse_width(pw)

class MCC(actionneur):
    def __init__(self, caract, pin, setup_ESC=False):
        super().__init__("mcc", pin)
        self.caract = caract
        
        if setup_ESC:
            self.set_pulse_width(1000)
            time.sleep(2)
            self.set_pulse_width(2000)
            time.sleep(1)
            self.set_pulse_width(1000)

    def commande_puissance(self, puis):
        pw = 0
        if puis > self.caract[1][0]:
            pw = self.caract[0][0]
            warnings.warn("Puissance trop importante !")
        elif puis <= self.caract[1][0] and puis > self.caract[1][1]:
            pw = (puis-self.caract[1][1])/(self.caract[1][0]-self.caract[1][1])*(self.caract[0][0]-self.caract[0][1]) + self.caract[0][1]
        elif puis <= self.caract[1][2] and puis >= self.caract[1][3]:
            pw = (puis-self.caract[1][3])/(self.caract[1][2]-self.caract[1][3])*(self.caract[0][2]-self.caract[0][3]) + self.caract[0][3]
        else :
            pw = self.caract[0][3]
            warnings.warn("Puissance trop faible !")

        self.set_pulse_width(pw)

class brushless(actionneur):
    def __init__(self, caract, pin_commande, pin_reverse, setup_ESC=False):
        super().__init__("brushless", pin_commande)
        GPIO.setup(pin_reverse, GPIO.OUT)
        self.pin_reverse = pin_reverse
        self.caract = caract

        if setup_ESC:
            self.set_pulse_width(1000)
            time.sleep(2)
            self.set_pulse_width(2000)
            time.sleep(1)
            self.set_pulse_width(1000)


    def commande_puissance(self, puis):
        pw = 0
        orientation = GPIO.LOW if puis < 0 else GPIO.HIGH
        puis = abs(puis)
        if puis > self.caract[1][0]:
            pw = self.caract[0][0]
            warnings.warn("Puissance trop importante !")
        elif puis <= self.caract[1][0] and puis >= self.caract[1][1]:
            pw = (puis-self.caract[1][1])/(self.caract[1][0]-self.caract[1][1])*(self.caract[0][0]-self.caract[0][1]) + self.caract[0][1]
        else:
            pw = self.caract[0][1]
            warnings.warn("Puissance trop faible !")

        GPIO.output(self.pin_reverse, orientation)
        self.set_pulse_width(pw)

HS_225BB = [[1840, 1107, 857], [270, 0, -90]]
MOTOR_YAW = [[1829, 1525, 1453, 1112], [1, 0, 0, -1]]
BRUSHLESS = [[1539, 1024], [1, 0]]
