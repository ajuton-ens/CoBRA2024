import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3Stamped
from rclpy.duration import Duration

import time

import time
#from adafruit_servokit import ServoKit #pour utiliser composant PCA9685
#kit = ServoKit(channels=16)
import warnings
from time import sleep
import smbus2
import pygame as p
from pyPS4Controller.controller import Controller
from gpiozero import LED


import threading

class Control(Node):
    def __init__(self):
        super().__init__('control')

        self.CONSIGNE_Z = 2

        Ts = 0.1

        # Altitude control
        P = 20.0
        I = 1.3
        D = 130.0
        N = 0.357

        self.a_alt = [P+D*N, P*N*Ts-2*P+I*Ts-2*D*N, P-P*N*Ts+I*N*Ts*Ts-I*Ts+D*N]
        self.b_alt = [1, N*Ts-2, 1-N*Ts]

        self.err_z = [0,0,0]
        self.commande_z = [0,0,0]

        # Rotation control

        self.pose_received_time = None
        self.pose_timeout = Duration(seconds=0.1)
        self.latest_pose = None
        self.latest_orientation = None

        self.subscription_pose = self.create_subscription(
            Vector3Stamped,
            '/pose_xyz',
            self.pose_callback,
            10  # Hz
        )

        self.subscription_orientation = self.create_subscription(
            Vector3Stamped,
            '/orientation_rpy',
            self.orientation_callback,
            10  # Hz
        )

        self.timer = self.create_timer(0.1, self.timer_callback)  # check every 50 ms

        myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
        myPCA9685 = PCA9685(myi2cbus) # Initialisation du générateur de PWM

        numeros_moteurs = {"brushless": [ 1, 2,3, 4], "MCC": [[6, 7], [7, 8]]}

        self.brushless = {}

        self.brushless["d"] = Brushless(myPCA9685,1)
        self.brushless["g"] = Brushless(myPCA9685,2)
        self.brushless["av"] = Brushless(myPCA9685,3)
        self.brushless["ar"] = Brushless(myPCA9685,4)
        self.pince = Pince(myPCA9685, 6)
        self.treuil = Treuil(myPCA9685, 7)

        # Parameters for MyController
        controller_params = {
            "interface": "/dev/input/js0",
            "connecting_using_ds4drv": False,
            "brushless": self.brushless,
            "pince": self.pince,
            "treuil": self.treuil
        }

        # Start a separate thread for the blocking function
        self.controller_thread = threading.Thread(target=self.controller_logic, args=(controller_params,))
        self.controller_thread.start()

        self.get_logger().info("Prêt - Initialisation réalisée")

    def controller_logic(self, controller_params):
        controller = MyController(**controller_params)
        controller.listen()

    def pose_callback(self, msg: Vector3Stamped):
        self.pose_received_time = self.get_clock().now()
        self.latest_pose = msg.vector  # Store the vector
        self.get_logger().debug('Pose received.')

    def orientation_callback(self, msg: Vector3Stamped):
        self.orientation_received_time = self.get_clock().now()
        self.latest_orientation = msg.vector

    def timer_callback(self):
        now = self.get_clock().now()

        if self.pose_received_time is not None and (now - self.pose_received_time) < self.pose_timeout:
            # ✅ Pose is recent (received within the last 0.1 s

            ####### Altitude control #######

            self.get_logger().info(f"Latest Z pose received: {self.latest_pose.z}")

            self.err_z[0] = self.CONSIGNE_Z - self.latest_pose.z

            self.commande_z[0] = self.a_alt[0]*self.err_z[0] + self.a_alt[1]*self.err_z[1] + self.a_alt[2]*self.err_z[2] - self.b_alt[1]*self.commande_z[1] - self.b_alt[2]*self.commande_z[2]

            self.brushless["av"].cmd_vit_pourcent(max(-100, min(self.commande_z[0], 100)))
            self.brushless["ar"].cmd_vit_pourcent(max(-100, min(self.commande_z[0], 100)))

            self.err_z[2] = self.err_z[1]
            self.err_z[1] = self.err_z[0]

            self.commande_z[2] = self.commande_z[1]
            self.commande_z[1] = self.commande_z[0]

        else:
            # ❌ Pose is too old or hasn't been received yet
            self.get_logger().warn('No recent pose.')
            # >>> PLACE YOUR LOGIC HERE (for when pose is stale or missing)
            #self.brushless["d"].cmd_vit_pourcent(0)
            #self.brushless["g"].cmd_vit_pourcent(0)
            self.brushless["av"].cmd_vit_pourcent(0)
            self.brushless["ar"].cmd_vit_pourcent(0)


def main(args=None):
    rclpy.init(args=args)
    node = Control()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\n[INFO] Program interrupted by user (Ctrl+C)")
    finally:
        print("[INFO] Stopping all motors...")

        # Stop all brushless motors
        for key, motor in node.brushless.items():
            motor.stop_mot()
            print(f"[INFO] Motor '{key}' stopped.")

        node.pince.cmd_vit_pourcent(0)
        node.treuil.cmd_vit_pourcent(0)

        node.destroy_node()
        rclpy.shutdown()
        print("[INFO] Shutdown complete.")


if __name__ == '__main__':
    main()

##############################################################################################################################
#################### Classes de controle des moteurs #########################################################################
##############################################################################################################################

class PCA9685:  # pour commander les sorties pwm
    def __init__(self, bus, address_PCA9685=0x40):
        self.available = False
        try:
            # DÉFINITION des registres (valeurs initiales)
            self.address_PCA9685 = address_PCA9685
            self.bus = bus
            self.MODE1 = 0x00  # self.REGISTRE = adresse_registre
            self.MODE2 = 0x01

            # liste de dictionnaires. Chaque dictionnaire definit les registres d'une sortie PWM de la PCA9685
            self.PWMs = [{"ON_L": 0x06, "ON_H": 0x07, "OFF_L": 0x08, "OFF_H": 0x09},
                         {"ON_L": 0x0A, "ON_H": 0x0B, "OFF_L": 0x0C, "OFF_H": 0x0D},
                         {"ON_L": 0x0E, "ON_H": 0x0F, "OFF_L": 0x10, "OFF_H": 0x11},
                         {"ON_L": 0x12, "ON_H": 0x13, "OFF_L": 0x14, "OFF_H": 0x15},
                         {"ON_L": 0x16, "ON_H": 0x17, "OFF_L": 0x18, "OFF_H": 0x19},
                         {"ON_L": 0x1A, "ON_H": 0x1B, "OFF_L": 0x1C, "OFF_H": 0x1D},
                         {"ON_L": 0x1E, "ON_H": 0x1F, "OFF_L": 0x20, "OFF_H": 0x21},
                         {"ON_L": 0x22, "ON_H": 0x23, "OFF_L": 0x24, "OFF_H": 0x25},
                         {"ON_L": 0x26, "ON_H": 0x27, "OFF_L": 0x28, "OFF_H": 0x29}]

            self.PRE_SCALE = 0xFE  # Numero du registre qui code la periode
            self.freqPWM_Hz = 50  # Frequence des PWM
            self.periodPWM = 1 / self.freqPWM_Hz  # 20 millisecondes
            # self.PCA9685_PRE_SCALE_VALUE = (round(25*10**6/(4096*self.freqPWM_Hz)-1)) #32  # configure la fréquence de la PWM sur tous les canaux
            self.PCA9685_PRE_SCALE_VALUE = 125

            # CONFIGURATION des registres du PCA9685
            self.bus.write_byte_data(self.address_PCA9685, self.MODE1, 0x10)
            self.bus.write_byte_data(self.address_PCA9685, self.PRE_SCALE, self.PCA9685_PRE_SCALE_VALUE)
            self.bus.write_byte_data(self.address_PCA9685, self.MODE1, 0x00)
            self.bus.write_byte_data(self.address_PCA9685, self.MODE2, 0x04)

            # Intervalles d’allumage et d’extinction (largeur d'impulsion) pour chaque PWM de self.PWMs.
            for PWM in self.PWMs:
                self.bus.write_byte_data(self.address_PCA9685, PWM["ON_L"], 0)
                self.bus.write_byte_data(self.address_PCA9685, PWM["ON_H"], 0x0)
                self.bus.write_byte_data(self.address_PCA9685, PWM["OFF_L"], 0x40)
                self.bus.write_byte_data(self.address_PCA9685, PWM["OFF_H"], 1)

            self.available = True

        except OSError as e:
            print(f"[ERROR] I2C communication error during PCA9685 initialization: {e}")
            self.available = False

    def commande_moteur_vitesse_us(self, temps_off_us, num_PWM):
        if not self.available:
            print("[WARNING] PCA9685 device not available. commande_moteur_vitesse_us ignored.")
            return
        points_off = temps_off_us * 4095 / (self.periodPWM * 1e6)
        temps_H = int(points_off // 256)
        temps_L = int(points_off % 256)
        try:
            self.bus.write_byte_data(self.address_PCA9685, self.PWMs[num_PWM]["OFF_L"], temps_L)
            self.bus.write_byte_data(self.address_PCA9685, self.PWMs[num_PWM]["OFF_H"], temps_H)
        except OSError as e:
            print(f"[ERROR] I2C communication error during commande_moteur_vitesse_us: {e}")


class Brushless:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_moteur : numero de la PWM de la PCA9685
    def __init__(self, PCA9685, num_moteur):
        self.num_moteur = num_moteur
        self.myPCA9685 = PCA9685
        self.valeur_repos = 1500  # valeur milieu de la commande => vitesse nulle
        self.cmd_vit_pourcent(0)

    def stop_mot(self):
        if not self.myPCA9685.available:
            print("[WARNING] PCA9685 device not available. stop_mot ignored.")
            return
        self.myPCA9685.commande_moteur_vitesse_us(0, self.num_moteur)

    def cmd_vit_pourcent(self, vitesse_pourcent):
        if not self.myPCA9685.available:
            print("[WARNING] PCA9685 device not available. cmd_vit_pourcent ignored.")
            return

        if vitesse_pourcent < -100:
            vitesse_pourcent = -100
        if vitesse_pourcent > 100:
            vitesse_pourcent = 100
        if 0 < vitesse_pourcent < 9:
            vitesse_pourcent = 4.5 + vitesse_pourcent / 2
        if 0 > vitesse_pourcent > -9:
            vitesse_pourcent = -4.5 + vitesse_pourcent / 2

        temps_etat_haut_us = self.valeur_repos + vitesse_pourcent * 5
        try:
            self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us, self.num_moteur)
        except OSError as e:
            print(f"[ERROR] I2C communication error in brushless cmd_vit_pourcent: {e}")


class Treuil:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_PWM    : numero de la PWM de la PCA9685 connectee a la modulation de vitesse

    def __init__(self, PCA9685, num_PWM):
        self.num_PWM = num_PWM
        self.myPCA9685 = PCA9685
        self.P_horaire = LED(24)
        self.P_antihoraire = LED(23)
        self.cmd_vit_pourcent(0)
    
    def stop(self):
        self.myPCA9685.commande_moteur_vitesse_us(0,self.num_PWM)
        self.P_horaire.off()
        self.P_antihoraire.off()

    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent >= 0:
            if vitesse_pourcent > 100:
                vitesse_pourcent = 100
            self.P_horaire.on()
            self.P_antihoraire.off()
            temps_etat_haut_us=200*vitesse_pourcent
            self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_PWM)
        else:
            if vitesse_pourcent < -100:
                vitesse_pourcent = -100
            self.P_horaire.off()
            self.P_antihoraire.on()
            temps_etat_haut_us=-200*vitesse_pourcent
            self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_PWM)
            
    def kill(self):
        self.P_horaire.close()
        self.P_antihoraire.close()

class Pince:
    # PCA9685    : instance de la classe PCA9685 utilisee
    # num_PWM    : numero de la PWM de la PCA9685 connectee a la modulation de vitesse

    def __init__(self, PCA9685, num_PWM):
        self.num_PWM = num_PWM
        self.myPCA9685 = PCA9685
        self.T_horaire = LED(8)
        self.T_antihoraire = LED(7)
        self.cmd_vit_pourcent(0)

    def stop(self):
        self.myPCA9685.commande_moteur_vitesse_us(0,self.num_PWM)
        self.T_horaire.off()
        self.T_antihoraire.off()
    
    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent >= 0:
            if vitesse_pourcent > 100:
                vitesse_pourcent = 100
            self.T_horaire.on()
            self.T_antihoraire.off()
            temps_etat_haut_us=200*vitesse_pourcent
            self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_PWM)
        else:
            if vitesse_pourcent < -100:
                vitesse_pourcent = -100
            self.T_horaire.off()
            self.T_antihoraire.on()
            temps_etat_haut_us=-200*vitesse_pourcent
            self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_PWM)
    
    def kill(self):
        self.T_horaire.close()
        self.T_antihoraire.close()


##############################################################################################################################
#################### Classe de controle de la mannette #######################################################################
##############################################################################################################################


class MyController(Controller):
    def __init__(self, **kwargs):
        # Extract the parameters for the parent Controller class
        controller_kwargs = {
            'interface': kwargs.get('interface', '/dev/input/js0'),
            'connecting_using_ds4drv': kwargs.get('connecting_using_ds4drv', False)
        }

        # Initialize the parent Controller class with only the expected arguments
        super().__init__(**controller_kwargs)

        # Store additional parameters as instance variables
        self.brushless = kwargs.get('brushless', {})
        self.treuil = kwargs.get('treuil', {})
        self.pince = kwargs.get('pince', {})
        self.vitesse_moy = 0
        self.vitesse_diff = 0
        self.arrêt = True


        # Attributs d'état 
        self.state = {
            'L1': 0,
            'R1': 0,
            'L2': 0, 
            'R2': 0,
            'L3_x': 0,
            'L3_y': 0,
            'R3_x': 0,
            'R3_y': 0,
            'X': 0, # attention c'est un X majuscule !
            'circle': 0,  
            'triangle': 0,
            'square': 0,
            'up_arrow': 0,
            'down_arrow': 0,
            'left_arrow': 0,
            'right_arrow': 0
        }
        
    def on_L2_press(self, value): #avancer
        self.state['L2'] = value

        if not self.arrêt :
            if value<0 :
                value = 0
            value = value*5/3200
            if value >50 :
                value = 50

            if value != 0 :
                print("La valeur de L2 est: ",value)

            self.vitesse_moy = value
            self.brushless["g"].cmd_vit_pourcent(self.vitesse_moy-self.vitesse_diff)
            self.brushless["d"].cmd_vit_pourcent(self.vitesse_moy+self.vitesse_diff)
        
    def on_R2_press(self,value): # reculer
        self.state['R2'] = value

        if not self.arrêt :
            if value<0 :
                value = 0
            value = value*5/3200
            if value >50 :
                value = 50

            if value != 0 :
                print("La valeur de R2 est: ",value)

            self.vitesse_moy = -value
            self.brushless["g"].cmd_vit_pourcent(self.vitesse_moy-self.vitesse_diff)
            self.brushless["d"].cmd_vit_pourcent(self.vitesse_moy+self.vitesse_diff)
    
    def on_R2_release(self):
        self.state['R2'] = 0
    def on_L2_release(self):
        self.state['L2'] = 0
 
    def on_L3_x_at_rest(self):
        self.state['L3_x'] = 0
        #print("L3 au milieu")
        
    def on_R1_press(self):
        self.state['R1'] = 1
        
    def on_R1_release(self):
        self.state['R1'] = 0
    
    def on_L3_right(self,value): #tourner à droite
        self.state['L3_x'] = value

        if not self.arrêt :
            if value<3200 :
                value = 0
            value = value*5/3200
            if value >50 :
                value = 50

            if value != 0 :
                print("L3 droite up value ="+str(value))

            self.vitesse_diff = value
            self.brushless["g"].cmd_vit_pourcent(self.vitesse_moy-self.vitesse_diff)
            self.brushless["d"].cmd_vit_pourcent(self.vitesse_moy+self.vitesse_diff)

    def on_L3_left(self,value): #tourner à gauche
        self.state['L3_x'] = -value

        if not self.arrêt :
            if value>-3200 :
                value = 0
            value = value*5/3200
            if value <-50 :
                value = -50
            
            if value != 0 :
                print("L3 gauche up value ="+str(value))

            self.vitesse_diff = value
            self.brushless["g"].cmd_vit_pourcent(self.vitesse_moy-self.vitesse_diff)
            self.brushless["d"].cmd_vit_pourcent(self.vitesse_moy+self.vitesse_diff)

    def on_L3_up(self,value): 
        self.state['L3_y'] = value
    def on_L3_down(self,value): 
        self.state['L3_y'] = -value

    def on_R3_up(self,value): # monter 
        self.state['R3_y'] = value

        if not self.arrêt :
            if value>-3200 :
                value = 0
            value = value*10/3200
            if value <-100 :
                value = -100
            
            if value != 0 :
                print("R3 up value ="+str(value))
            
            # self.brushless["av"].cmd_vit_pourcent(value)
            # self.brushless["ar"].cmd_vit_pourcent(value)
    
    def on_R3_down(self,value): # descendre
        self.state['R3_y'] = -value

        if not self.arrêt :
            if value<3200 :
                value = 0
            value = value*10/3200
            if value >100 :
                value = 100

            if value != 0 :
                print("R3 down value ="+str(value))
            
            # self.brushless["av"].cmd_vit_pourcent(value)
            # self.brushless["ar"].cmd_vit_pourcent(value)
        
        
    
        
        
    def on_x_press(self):
        self.state['X'] = 1

        self.brushless['ar'].stop_mot()
        self.brushless['av'].stop_mot()
        self.brushless['g'].stop_mot()
        self.brushless['d'].stop_mot()
        self.pince.cmd_vit_pourcent(0)
        self.pince.cmd_vit_pourcent(0)

        self.arrêt = True
        print(self.arrêt)
        
    def on_circle_press(self):
        self.state['circle'] = 1

        #self.brushless["ar"].cmd_vit_pourcent(0)
        #self.brushless["av"].cmd_vit_pourcent(0)
        self.brushless["g"].cmd_vit_pourcent(0)
        self.brushless["d"].cmd_vit_pourcent(0)
        self.arrêt = False
        print(self.arrêt)

    def on_triangle_press(self):
        self.state['triangle'] = 1
    def on_triangle_release(self):
        self.state['triangle'] = 0
    def on_R3_x_at_rest(self):
        self.state['R3_x'] = 0

    def on_R3_right(self,value):
        self.state['R3_x'] = value

    def on_R3_left(self,value):
        self.state['R3_x'] = -value

    def on_L3_up(self,value):
        self.state['L3_y'] = value

    def on_L3_down(self,value):
        self.state['L3_y'] = -value

    def on_circle_release(self):
        self.state['circle'] = 0

    def on_L1_press(self):
        self.state['L1'] = 1

    def on_L1_release(self):
        self.state['L1'] = 0

    def on_x_release(self):
        self.state['X'] = 0

    def on_L3_y_at_rest(self):
        self.state['L3_y'] = 0
        self.vitesse_diff = 0

    def on_R3_y_at_rest(self):
        self.state['R3_y'] = 0



    # ------------
    # PARTIE ENZO
    # ------------

    # TREUIL
    def on_square_press(self):
        self.state['square'] = 1

        if self.sens_treuil == "bas" :
            while self.contact == True :
                self.treuil.cmd_vit_pourcent(-100)
            while self.contact == False :
                self.treuil.cmd_vit_pourcent(-100)
            self.sens_treuil = "haut"
        elif self.sens_treuil == "haut" :
            while self.contact == True :
                self.treuil.cmd_vit_pourcent(100)
            while self.contact == False :
                self.treuil.cmd_vit_pourcent(100)
            self.sens_treuil = "bas"
        else :  
            pass


    def on_up_arrow_press(self):
        self.state['up_arrow'] = 1

        #brushless["t"].cmd_vit_pourcent(50)
        print("Montée treuil")
        if not self.arrêt:
            self.treuil.cmd_vit_pourcent(100)
            pass
            

    def on_down_arrow_press(self):
        self.state['down_arrow'] = 1

        #brushless["t"].cmd_vit_pourcent(-50)
        print("Descente treuil")
        if not self.arrêt:
            self.treuil.cmd_vit_pourcent(-100)
            pass

    
    def on_up_down_arrow_release(self):
        self.state['up_arrow'] = 0
        self.state['down_arrow'] = 0

        self.treuil.cmd_vit_pourcent(0)
        print("Arrêt treuil")

    # PINCE
    def on_right_arrow_press(self):
        self.state['right_arrow'] = 1

        if not self.arrêt:
            self.pince.cmd_vit_pourcent(100)
            print("Fermeture pince")

    def on_left_arrow_press(self):
        self.state['left_arrow'] = 1

        if not self.arrêt:
            self.pince.cmd_vit_pourcent(-100)
            print("Ouverture pince")
    
    def on_left_right_arrow_release(self):
        self.state['right_arrow'] = 0
        self.state['left_arrow'] = 0

        self.pince.cmd_vit_pourcent(0)
        print("Arrêt pince")

#La bibliothèque que nous avons écrite se base sur la bibliothèque adafruit_servokit