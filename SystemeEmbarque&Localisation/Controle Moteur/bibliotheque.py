from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)
import warnings
import time

class Actionneur:
    def __init__(self, type, pin):
        self.type = None
        self.pin = pin

    def pulse_width_to_thr(self, pw):
        return (pw - 1445)/(2170 - 1445)

    def set_pulse_width(self, pw):
        thr = self.pulse_width_to_thr(pw)
        kit.continuous_servo[self.pin].throttle = thr

class Servo(actionneur):
    def __init__(self, caract, pin):
        super.__init__("servo", pin)
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
    def __init__(self, caract, pin):
        super.__init__("mcc", pin)
        self.caract = caract

    def commande_puissance(self, puis):
        pw = 0
        if puis > self.caract[1][0]:
            pw = self.caract[0][0]
            warnings.warn("Puissance trop importante !")
        elif puis <= self.caract[1][0] and puis > self.caract[1][1]:
            pw = (puis-self.caract[1][1])/(self.caract[1][0]-self.caract[1][1])*(self.caract[0][0]-self.caract[0][1]) + self.caract[0][1]
        elif puis <= self.caract[1][1] and puis > self.caract[1][2]:
            pw = 1450
        elif puis <= self.caract[1][2] and puis >= self.caract[1][3]:
            pw = (puis-self.caract[1][3])/(self.caract[1][2]-self.caract[1][3])*(self.caract[0][2]-self.caract[0][3]) + self.caract[0][3]
        else :
            pw = self.caract[0][3]
            warnings.warn("Puissance trop faible !")

        self.set_pulse_width(pw)

class Brushless(actionneur):
    def __init__(self, caract, pin):
        super.__init__("brushless", pin)
        self.caract = caract

        self.set_pulse_width(self.pin, 1000)
        time.sleep(2)
        self.set_pulse_width(self.pin, 2000)
        time.sleep(1)
        self.set_pulse_width(self.pin, 1000)


    def commande_puissance(self, puis):
        pw = 0
        if puis > self.caract[1][0]:
            pw = self.caract[0][0]
            warnings.warn("Puissance trop importante !")
        elif puis <= self.caract[1][0] and puis > self.caract[1][1]:
            pw = (puis-self.caract[1][1])/(self.caract[1][0]-self.caract[1][1])*(self.caract[0][0]-self.caract[0][1]) + self.caract[0][1]
        else:
            pw = self.caract[0][1]
            warnings.warn("Puissance trop faible !")

        self.set_pulse_width(pw)

HS_225BB = [[1840, 1107, 857], [270, 0, -90]]
MOTOR_YAW = [[1829, 1560, 1445, 1112], [1, 0, 0, -1]]
BRUSHLESS = [[1539, 1024], [1, 0]]
