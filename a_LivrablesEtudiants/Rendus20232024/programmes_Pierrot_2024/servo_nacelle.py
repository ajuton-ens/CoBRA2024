import time
from pyPS4Controller.controller import Controller
from adafruit_servokit import ServoKit

angle_min = 0
angle_max = 130

kit = ServoKit(channels=16)
kit.servo[0].angle = angle_min
kit.servo[15].angle = 45

class MyController(Controller):
    def on_L3_up(self, value):
        kit.servo[15].angle = 45 + value * 36/32767
    
    def on_L3_down(self,value):
        kit.servo[15].angle = 45 + value * 94/32767
        
    def on_R3_up(self,value):
        quotient = abs(value/32767)
        kit.servo[0].angle = angle_min+(angle_max-angle_min)*quotient
        
    def on_R3_down(self,value):
        quotient = abs(value/32767)
        kit.servo[0].angle = angle_min+(angle_max-angle_min)*quotient
    
    
    
    
MyController(interface="/dev/input/js0", connecting_using_ds4drv=False).listen()