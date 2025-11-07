import time
from pyPS4Controller.controller import Controller
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
kit.servo[0].set_pulse_width_range(700, 5000)
kit.servo[1].set_pulse_width_range(700, 5000)
kit.servo[2].set_pulse_width_range(700, 5000)
kit.servo[0].angle = 45
kit.servo[1].angle = 45
kit.servo[2].angle = 45
class MyController(Controller):
    def on_L3_left(self, value):
        kit.servo[0].angle = 45 + value * 44/32767
    
    def on_L3_right(self,value):
        kit.servo[0].angle = 45 + value * 44/32767
        
    def on_R3_left(self, value):
        kit.servo[1].angle = 45 + value * 44/32767
        kit.servo[2].angle = 45 + value * 44/32767
    
    def on_R3_right(self, value):
        kit.servo[1].angle = 45 + value * 44/32767
        kit.servo[2].angle = 45 + value * 44/32767
    
MyController(interface="/dev/input/js0", connecting_using_ds4drv=False).listen()

