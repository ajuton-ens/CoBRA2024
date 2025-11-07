import numpy as np
import smbus2
import time
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import sensors_lib.MyBNO055 as MyBNO055
import sensors_lib.MyTFLuna as MyTFLuna
import sensors_lib.MyTag  as MyTag
PITCH_INDEX    = 0
ROLL_INDEX     = 1
HEADING_INDEX  = 2
X_INDEX = 3
Y_INDEX = 4
Z_INDEX = 5

NB_MEASURES = 10

current_measures = [["initialising",1] for i in range(0,6)]
current_measures[PITCH_INDEX][0] = "PITCH"
current_measures[ROLL_INDEX][0] = "ROLL"
current_measures[HEADING_INDEX][0] = "HEADING"
current_measures[X_INDEX][0] = "X"
current_measures[Y_INDEX][0] = "Y"
current_measures[Z_INDEX][0] = "Z"

def get_current_measures(measures_array):
     global current_measures

     current_measures[PITCH_INDEX][1]   = measures_array[PITCH_INDEX]
     current_measures[ROLL_INDEX][1]    = measures_array[ROLL_INDEX]
     current_measures[HEADING_INDEX][1] = measures_array[HEADING_INDEX]
     current_measures[X_INDEX][1]       = measures_array[X_INDEX]
     current_measures[Y_INDEX][1]       = measures_array[Y_INDEX]
     current_measures[Z_INDEX][1]       = measures_array[Z_INDEX]

def mergemeas(measures_matrix,aa):
     global PITCH_INDEX
     global ROLL_INDEX
     global X_INDEX
     global Y_INDEX
     global Z_INDEX
     global current_measures
     lidar = MyTFLuna.LidarTFLuna()
     i2cbus = smbus2.SMBus(1) 
     mybno = MyBNO055.BNO055(i2cbus)
     #mybno.calibration()
     measures_array = np.zeros((6))
     tag_camera = MyTag.Tag()

     heading_offset = 0.0
     heading_initialized = False
     
     while True:
          # Mesures BNO055
          angle_euler = mybno.read_euler()
          pitch = angle_euler["pitch"]
          roll = angle_euler["roll"]
          heading_bno_raw = angle_euler["heading"]

          # Appliquer la correction si initialisée
          heading_corrected = (heading_bno_raw + heading_offset) % 360

          # Stocker dans le tableau
          measures_array[PITCH_INDEX] = pitch
          measures_array[ROLL_INDEX] = roll
          measures_array[HEADING_INDEX] = heading_corrected

          # LIDAR + calcul Z
          distance = lidar.read_distance()
          dist_z = abs(distance * np.cos(np.radians(roll)) * np.cos(np.radians(pitch)))
          measures_array[Z_INDEX] = dist_z

          # Lecture caméra
          try:
               localisation_result = tag_camera.localisation()
               if localisation_result is not None:
                    x_cam, y_cam, z_cam, heading_cam = localisation_result

                    # Initialisation une fois si heading non encore corrigé
                    if not heading_initialized:
                         heading_offset = (heading_cam - heading_bno_raw) % 360
                         heading_initialized = True
                         print(f"🔧 Initialisation heading BNO : offset = {heading_offset:.2f}°")

               else:
                    x_cam, y_cam = 0.0, 0.0

          except Exception as e:
               print("Erreur caméra:", e)
               x_cam, y_cam = 0.0, 0.0
          measures_array[X_INDEX] = x_cam
          measures_array[Y_INDEX] = y_cam
          # Mise à jour du tableau
          measures_matrix[:,:-1] = measures_matrix[:,1:]
          measures_matrix[:,-1] = measures_array

          get_current_measures(measures_array)
          time.sleep(0.1)
          aa[0] += 1
     

if __name__ == "__main__":
     import userinput_lib.v15_test_commandes_TUI as TUI
     measures_matrix = np.zeros((6,NB_MEASURES))
     mergemeas(measures_matrix,TUI.aa)