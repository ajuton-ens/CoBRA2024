#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Derniere modif: 02/05/2025

import smbus2
import cobra_pca9685_v09temp as pca9685
import curses

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = pca9685.PCA9685(myi2cbus) # Initialisation du générateur de PWM

brushless_config = { "propulsion":   {"valeur_repos_us": 1.5*10**3, "seuil_vitesse_neg_pourcent": -4.5, "seuil_vitesse_pos_pourcent": 4.5}
            }

#FUTABA S3107 : 2.37ms correspond a 0deg du systeme.
#FUTABA S3107 : 1.92ms correspond a 90deg du systeme.
#FUTABA S3107 : 1.38ms correspond a 180deg du systeme.

servo_config = { "cerceau":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286},
                 "axe":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286}
            }

print(brushless_config["propulsion"])

brushless = {}
servo = {}
mcc = {}

servo["cerceau"]= pca9685.servo(myPCA9685,4, servo_config["cerceau"])
servo["axe"]= pca9685.servo(myPCA9685,5, servo_config["axe"])
brushless["gauche"] = pca9685.brushless(myPCA9685,6,brushless_config["propulsion"])
brushless["droite"] = pca9685.brushless(myPCA9685,7,brushless_config["propulsion"])

print("Prêt - Initialisation réalisée")


brushless_list = [list(tup) for tup in list(brushless.items())]
servo_list     = [list(tup) for tup in list(servo.items())]
mcc_list     = [list(tup) for tup in list(mcc.items())]
PAGE_BRUSHLESS = 0
PAGE_SERVO = 1
PAGE_MCC = 2
PAGE_WIDTH = 20
pages = [brushless_list, servo_list, mcc_list]

def get_motor_value(motor, page_current):
    match page_current:
        case page if page==PAGE_BRUSHLESS:
            return motor.vitesse_pourcent
        case page if page==PAGE_SERVO:
            return motor.angle_deg
        case page if page==PAGE_MCC:
            return motor.vitesse_pourcent

def set_motor_value(motor, page_current, val):
    match page_current:
        case page if page==PAGE_BRUSHLESS:
            motor.cmd_vit_pourcent(val)
        case page if page==PAGE_SERVO:
            motor.cmd_angle_deg(val)
        case page if page==PAGE_MCC:
            motor.cmd_vit_pourcent(val)

def main(stdscr):
    page_current = 0
    height, width = stdscr.getmaxyx()
    CURSOR_Y_MAX=len(pages[page_current])
    cursor_y=0
    key=0
    input_nb=""

    # Boucle_continue/principale
    while key != ord('q'):
        match key:
            case curses.KEY_DOWN:
                if (cursor_y >= CURSOR_Y_MAX-1):
                    page_current = (page_current+1)%len(pages)
                    CURSOR_Y_MAX=len(pages[page_current])
                    cursor_y = 0
                else:
                    cursor_y = cursor_y+1
            case curses.KEY_UP:
                if (cursor_y <= 0):
                    page_current = (page_current-1)%len(pages)
                    CURSOR_Y_MAX=len(pages[page_current])
                    cursor_y = CURSOR_Y_MAX-1
                else:
                    cursor_y = cursor_y-1
            case curses.KEY_LEFT:
                motor = pages[page_current][cursor_y][1]
                motor_value = get_motor_value(motor,page_current)
                set_motor_value(motor,page_current,motor_value-1)
            case curses.KEY_RIGHT:
                motor = pages[page_current][cursor_y][1]
                motor_value = get_motor_value(motor,page_current)
                set_motor_value(motor,page_current,motor_value+1)
            case num if chr(key).isdigit():
                input_nb+=chr(key)
            case minus if minus == ord('-'):
                if (input_nb == ""):
                    input_nb += chr(key)
            case curses.KEY_ENTER | 10 | 13:
                set_motor_value(motor,page_current,int(input_nb))
                input_nb=""
        
        stdscr.clear()
        for page_i in range(0,len(pages)):
            for motor_i in range(0, len(pages[page_i])):
                motor_dict = pages[page_i][motor_i]
                stdscr.addstr(motor_i, PAGE_WIDTH*page_i+1, str(motor_dict[0]))
                stdscr.addstr(motor_i, PAGE_WIDTH*page_i+10, str(get_motor_value(motor_dict[1],page_i)))
        stdscr.addstr(height-2, 10, str(input_nb))
        stdscr.move(cursor_y,PAGE_WIDTH*page_current)
        stdscr.refresh()
        key = stdscr.getch()

curses.wrapper(main)

"""
        nom_type = input("Donner type")
        if nom_type == "s":
            nom_servo=input("Donner nom servo:")
            if nom_servo in servo:
                commande_angle_deg=int(input("Donner la commande d'angle du servomoteur en degres (entre -90 et 90):"))
                servo[nom_servo].cmd_angle_deg(commande_angle_deg)
            else:
                print("nom de servomoteur invalide !")
        elif nom_type == "b":
            nom_brushless=input("Donner nom brushless:")
            if nom_brushless in brushless:
                commande_vitesse_pourcentage=int(input("Donner la commande de vitesse du moteur en pourcentage (entre -100 et 100):"))
                brushless[nom_brushless].cmd_vit_pourcent(commande_vitesse_pourcentage)
            else:
                print("nom de brushless invalide !")
    
"""