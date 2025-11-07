from library import *
from pyPS4Controller.controller import Controller

HS_225BB = [[1840, 1107, 857], [270, 0, -90]]
MOTOR_YAW = [[1829, 1525, 1453, 1112], [1, 0, 0, -1]]
BRUSHLESS = [[1539, 1024], [1, 0]]

PS4_JOYSTICK_COURSE = 32767

init(2)
init(1)

class MyController(Controller):
    def on_L3_up(self, value):
        if value > 0:
            angle = value*(HS_225BB[1][0] - HS_225BB[1][1])/PS4_JOYSTICK_COURSE
        else:
            angle = value*(HS_225BB[1][1] - HS_225BB[1][2])/PS4_JOYSTICK_COURSE
        pw = impulsion_commande_servo(HS_225BB, angle)
        set_pulse_width(0, pw)
        
    def on_L3_down(self,value):
        if value > 0:
            angle = value*(HS_225BB[1][0] - HS_225BB[1][1])/PS4_JOYSTICK_COURSE
        else:
            angle = value*(HS_225BB[1][1] - HS_225BB[1][2])/PS4_JOYSTICK_COURSE
        pw = impulsion_commande_servo(HS_225BB, angle)
        set_pulse_width(0, pw)
        
    def on_L3_right(self, value):
        puis = value/PS4_JOYSTICK_COURSE
        pw = impulsion_commande_moteur(MOTOR_YAW, puis)
        set_pulse_width(2, pw)
        
    def on_L3_left(self,value):
        puis = value/PS4_JOYSTICK_COURSE
        pw = impulsion_commande_moteur(MOTOR_YAW, puis)
        set_pulse_width(2, pw)
                  
    def on_R3_up(self,value):
        puis = abs(value/PS4_JOYSTICK_COURSE)
        pw = impulsion_commande_moteur(BRUSHLESS, puis)
        set_pulse_width(1, pw)
        
    def on_R3_down(self,value):
        puis = abs(value/PS4_JOYSTICK_COURSE)
        pw = impulsion_commande_moteur(BRUSHLESS, puis)
        set_pulse_width(1, pw)
    
MyController(interface="/dev/input/js0", connecting_using_ds4drv=False).listen()