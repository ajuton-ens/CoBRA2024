import numpy as np
import smbus2
import sensors_lib.MyBNO055 as MyBNO055
import time
import sensors_lib.MyTFLuna as MyTFLuna

lidar = MyTFLuna.LidarTFLuna()
i2cbus = smbus2.SMBus(1) 
mybno = MyBNO055.BNO055(i2cbus)
mybno.calibration()



while True:
     distanceh = lidar.read_distance()
     print(f"La distance mesurée par le télémètre infrarouge est: {distanceh}cm")
     angle_euler = mybno.read_euler()
     angle_bno = np.array([angle_euler["pitch"], angle_euler["roll"], angle_euler["heading"]])
     print("Angle BNO055:", angle_bno)
     time.sleep(0.1)

        
