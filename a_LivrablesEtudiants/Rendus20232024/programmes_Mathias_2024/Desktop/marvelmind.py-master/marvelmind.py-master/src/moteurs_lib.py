from adafruit_servokit import ServoKit
import warnings
import time
import sys, tty, termios




class Servo:
    def __init__(self, angles, pwm, HAT, channel):
        """Defini une classe servo avec les angles [max, repos, min] et pwm [pulse_max, pulse_repos, pulse_min]"""
        self.angle_max = angles[0]
        self.angle_repos = angles[1]
        self.angle_min = angles[2]

        self.pwm_max = pwm[0]
        self.pwm_repos = pwm[1]
        self.pwm_min = pwm[2]

        self.hardware = HAT
        
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
        self.hardware.continuous_servo[self.channel].throttle = thr


class BrushlessMotor:
    def __init__(self, HAT, channel):
        self.hardware = HAT
        self.channel = channel

    def initialisation(self):
        self.hardware.continuous_servo[self.channel].throttle = -1

    def calculate_imp(self, speed):  # DE 0 A 1
        """Fonction permettant de passer de [0,1] à [-1,1] (zone morte entre -1 et -0.58)"""
        
        return 1.7*speed - 0.7
    
    def set_speed(self, speed):
        """Envoie le signal PWM de largeur d'impulsion pw sur le channel du servo"""
        self.hardware.continuous_servo[self.channel].throttle = self.calculate_imp(speed)


class MCC:
    def __init__(self, HAT, channel):
        self.hardware = HAT

        self.channel = channel

    def initialisation(self):
        self.hardware.continuous_servo[self.channel].throttle = 0.05

    def calculate_imp(self, speed):  # DE 0 A 1
        """Calcule la largeur d'impulsion correspondant a la speed puis pour le moteur brushless"""
        if speed > 1:
            pw = self.pwm_max_forw
        elif speed <= 1 and speed > 0:
            pw = speed*(self.pwm_max_forw-self.pwm_min_forw) + self.pwm_min_forw
        elif speed <= 0 and speed >= -1:
            pw = (speed+1)*(self.pwm_min_back-self.pwm_max_back) + self.pwm_max_back
        else :
            pw = self.pwm_max_back
            
        return pw
    
    def set_speed(self, speed):
        """Envoie le signal PWM de largeur d'impulsion pw sur le channel du servo"""
        # speed = speed + 0.05
        if speed >= 1:
            speed = 1
        elif speed <= -1:
            speed = -1
        self.hardware.continuous_servo[self.channel].throttle = speed

    def stop(self):
        """Envoie le signal PWM de largeur d'impulsion pw sur le channel du servo"""
        self.hardware.continuous_servo[self.channel].throttle = 0.05

