# -*- coding:utf-8 -*-
import sys
import os
import time
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from DFRobot_bmm350 import *

I2C_BUS = 0x01
bmm350 = DFRobot_bmm350_I2C(I2C_BUS, 0x14)

# --- CONFIGURATION DE VOS VALEURS DE CALIBRATION ---
X_MIN, X_MAX = -30.0, 24.0
Y_MIN, Y_MAX = 0, 56.0

# Calcul automatique des décalages (Offsets)
X_OFFSET = (X_MAX + X_MIN) / 2.0  # Vaut 0.0
Y_OFFSET = (Y_MAX + Y_MIN) / 2.0  # Vaut 25.0

def setup():
  while BMM350_CHIP_ID_ERROR == bmm350.sensor_init():
    print("sensor init error, please check connect")
    print("bmm350.sensor_init()")
    print(BMM350_CHIP_ID_ERROR) 
    time.sleep(1)

  bmm350.set_operation_mode(BMM350_NORMAL_MODE)
  bmm350.set_preset_mode(BMM350_PRESETMODE_HIGHACCURACY, BMM350_DATA_RATE_25HZ)
  bmm350.set_measurement_XYZ()
  
def loop():
  geomagnetic = bmm350.get_geomagnetic_data()
  raw_x = geomagnetic[0]
  raw_y = geomagnetic[1]
  raw_z = geomagnetic[2]
  
  # 1. Correction des données brutes avec vos offsets
  calibrated_x = raw_x - X_OFFSET
  calibrated_y = raw_y - Y_OFFSET
  
  # 2. Calcul du cap (Compass Degree) sur 360° avec les valeurs corrigées
  # Remarque : selon l'orientation de votre capteur, vous pouvez inverser 
  # l'ordre ou le signe de X et Y pour correspondre au Nord de votre pièce.
  compass = math.atan2(calibrated_x, calibrated_y)
  
  # Conversion des radians en degrés
  degree = compass * 180.0 / math.pi -175
  
  # Ajustement pour obtenir une plage propre de 0 à 360°
  if degree < 0:
    degree += 360.0
    
  print("Brut      -> X: %d uT | Y: %d uT" % (raw_x, raw_y))
  print("Calibré   -> X: %.1f uT | Y: %.1f uT" % (calibrated_x, calibrated_y))
  print("Angle Nord: %.2f °" % degree)
  print("-" * 40)
  
  time.sleep(0.5)

if __name__ == "__main__":
  setup()
  while True:
    loop()