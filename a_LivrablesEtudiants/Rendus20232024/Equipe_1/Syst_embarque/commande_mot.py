# -*- coding: utf-8 -*-

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16, address=0x7f)
import warnings
import time


class Servo:
    def __init__(self, angles, pwm, channel):
        """Defini une classe servo avec les angles [max, repos, min] et pwm [pulse_max, pulse_repos, pulse_min]"""
        self.angle_max = angles[0]
        self.angle_repos = angles[1]
        self.angle_min = angles[2]

        self.pwm_max = pwm[0]
        self.pwm_repos = pwm[1]
        self.pwm_min = pwm[2]
        
        self.channel = channel

    def calculate_imp(self,angle):
        """Calcule la largeur d'impulsion correspondant a l'angle angle"""
        pw = 0
        if angle > self.angle_max:
            pw = self.pwm_max
            warnings.warn("Angle trop important !")
        elif angle <= self.angle_max and angle > self.angle_repos:
            pw = (angle-self.angle_repos)/(self.angle_max-self.angle_repos)*(self.pwm_max-self.pwm_repos) + self.pwm_repos
        elif angle <= self.angle_repos and angle >= self.angle_min:
            pw = (angle-self.angle_min)/(self.angle_repos-self.angle_min)*(self.pwm_repos-self.pwm_min) + self.pwm_min
        else :
            pw = self.pwm_min
            warnings.warn("Angle trop faible !")
        return pw
    
    def set_angle(self, angle):
        """Envoie le signal PWM de largeur d'impulsion pw sur le channel du servo"""
        pw = self.calculate_imp(angle)
        thr = (pw - 1445)/(2170 - 1445)  # necessite une conversion pour etre compréhensible pour le HAT
        kit.continuous_servo[self.channel].throttle = thr


class BrushlessMotor:
    def __init__(self, pwm, channel):
        self.pwm_max = pwm[0]
        self.pwm_min = pwm[1]

        self.channel = channel

    def initialisation(self):
        thr = (1000 - 1445)/(2170 - 1445)  # necessite une conversion pour etre compréhensible pour le HAT
        kit.continuous_servo[self.channel].throttle = thr

    def calculate_imp(self, speed):  # DE 0 A 1
        """Calcule la largeur d'impulsion correspondant a la speed puis pour le moteur brushless"""
        if speed > 1:
            pw = self.pwm_max
            warnings.warn("speed trop importante !")
        elif speed <= 1 and speed > 0:
            pw = speed*(self.pwm_max-self.pwm_min) + self.pwm_min
        else:
            pw = self.pwm_min
            warnings.warn("speed trop faible !")
            
        return pw
    
    def set_speed(self, speed):
        """Envoie le signal PWM de largeur d'impulsion pw sur le channel du servo"""
        pw = self.calculate_imp(speed)
        thr = (pw - 1445)/(2170 - 1445)  # necessite une conversion pour etre compréhensible pour le HAT
        kit.continuous_servo[self.channel].throttle = thr


class MCC:
    def __init__(self, pwm, channel):
        self.pwm_max_forw = pwm[0]
        self.pwm_min_forw = pwm[1]
        self.pwm_max_back = pwm[3]
        self.pwm_min_back = pwm[2]

        self.channel = channel

    def initialisation(self):
        pwm_init = 1550
        thr = (pwm_init - 1445)/(2170 - 1445)  # necessite une conversion pour etre compréhensible pour le HAT
        kit.continuous_servo[self.channel].throttle = thr

    def calculate_imp(self, speed):  # DE 0 A 1
        """Calcule la largeur d'impulsion correspondant a la speed puis pour le moteur brushless"""
        if speed > 1:
            pw = self.pwm_max_forw
            warnings.warn("Puissance trop importante !")
        elif speed <= 1 and speed > 0:
            pw = speed*(self.pwm_max_forw-self.pwm_min_forw) + self.pwm_min_forw
        elif speed <= 0 and speed >= -1:
            pw = (speed+1)*(self.pwm_min_back-self.pwm_max_back) + self.pwm_max_back
        else :
            pw = self.pwm_max_back
            warnings.warn("Puissance trop faible !")
            
        return pw
    
    def set_speed(self, speed):
        """Envoie le signal PWM de largeur d'impulsion pw sur le channel du servo"""
        pw = self.calculate_imp(speed)
        thr = (pw - 1445)/(2170 - 1445)  # necessite une conversion pour etre compréhensible pour le HAT
        kit.continuous_servo[self.channel].throttle = thr

    def stop(self):
        """Envoie le signal PWM de largeur d'impulsion pw sur le channel du servo"""
        pw = 1550
        thr = (pw - 1445)/(2170 - 1445)  # necessite une conversion pour etre compréhensible pour le HAT
        kit.continuous_servo[self.channel].throttle = thr





servo = Servo([270, 0, -90], [1840, 1107, 857], 0)
main_motor = BrushlessMotor([1539, 1024], 5)
back_motor = MCC([1829, 1600, 1500, 1112], 6)

main_motor.initialisation()
back_motor.initialisation()
time.sleep(2.5)
back_motor.stop()
servo.set_angle(0)
