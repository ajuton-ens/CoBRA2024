#!/usr/bin/env python3
import numpy as np
import time
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import sensors_lib.MyBNO055 as MyBNO055
import sensors_lib.MyTFLuna as MyTFLuna
import sensors_lib.MyTag    as MyTag
import FAKE_LIB.smbus2 as smbus2
import config

class MyMergeMeas:
     def __init__(self):
          self.lidar      = MyTFLuna.LidarTFLuna()
          self.i2cbus     = smbus2.SMBus(1) 
          self.mybno      = MyBNO055.BNO055(self.i2cbus)
          #mybno.calibration()
          self.tag_camera = MyTag.Tag()
          
          self.heading_offset = 0
          self.last_time = time.time()
          self.last_measures_array = np.zeros((config.NB_AXES))
     
     def do_merge_meas(self,current_time):
          measures_array = np.zeros((config.NB_AXES))

          # Mesures BNO055
          angle_euler = self.mybno.read_euler()
          pitch = angle_euler["roll"] 
          if angle_euler["pitch"] <0 :
               roll = -(angle_euler["pitch"]+180-8)
          else:
               roll = -(angle_euler["pitch"]-180+9)
          heading_bno_raw = angle_euler["heading"]
          heading_corrected = (heading_bno_raw+self.heading_offset-180)%360

          # Lecture caméra
          try:
               localisation_result = self.tag_camera.localisation()
               if localisation_result is not None:
                    x_cam, y_cam, z_cam, heading_cam = localisation_result
                    # Correction de l'angle de la caméra                 
                    if current_time - self.last_time >= 1:
                         self.last_time = current_time
                         self.heading_offset = (heading_cam - heading_bno_raw) % 360
               else:
                    x_cam, y_cam = None, None
          except Exception as e:
               print("Erreur caméra:", e)
               x_cam, y_cam = None, None

          # Stocker dans le tableau 1D
          measures_array[config.PITCH_INDEX]   = pitch
          measures_array[config.ROLL_INDEX]    = roll + 3
          measures_array[config.HEADING_INDEX] = heading_corrected
          measures_array[config.X_INDEX]       = x_cam
          measures_array[config.Y_INDEX]       = y_cam

          # LIDAR + calcul Z
          distance = self.lidar.read_distance()
          dist_z = abs(distance * np.cos(np.radians(roll)) * np.cos(np.radians(pitch)))
          measures_array[config.Z_INDEX] = dist_z
          
          return measures_array

     def update_measures(self,current_time):
          measures_array = self.do_merge_meas(current_time)
          measures_array[config.X_INDEX] = self.last_measures_array[config.X_INDEX] if measures_array[config.X_INDEX] is None else measures_array[config.X_INDEX]
          measures_array[config.Y_INDEX] = self.last_measures_array[config.Y_INDEX] if measures_array[config.Y_INDEX] is None else measures_array[config.Y_INDEX]
          
          return measures_array