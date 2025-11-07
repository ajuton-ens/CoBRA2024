import numpy as np
import smbus2
import sensors_lib.MyBNO055 as MyBNO055
import time
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
     
     while True:
          distance = lidar.read_distance()
          angle_euler = mybno.read_euler()
          measures_array[PITCH_INDEX] = angle_euler["pitch"]
          measures_array[ROLL_INDEX] = angle_euler["roll"]
          measures_array[HEADING_INDEX] = angle_euler["heading"]

          dist_z = abs(distance*np.cos(angle_euler["roll"]*np.pi/180)*np.cos(angle_euler["pitch"]*np.pi/180))
          measures_array[Z_INDEX] = dist_z
           # Mesures caméra
          try:
               x_cam, y_cam, z_cam, heading_cam = tag_camera.localisation()
          except Exception as e:
            print("Erreur caméra:", e)
            x_cam, y_cam = 0.0, 0.0
          measures_array[X_INDEX] = x_cam
          measures_array[Y_INDEX] = y_cam
          measures_matrix[:,:-1] = measures_matrix[:,1:]
          measures_matrix[:,-1] =  measures_array

          get_current_measures(measures_array)
          time.sleep(0.1)
          aa[0]+=1
     

if __name__ == "__main__":
     import userinput_lib.v15_test_commandes_TUI as TUI
     measures_matrix = np.zeros((6,NB_MEASURES))
     mergemeas(measures_matrix,TUI.aa)