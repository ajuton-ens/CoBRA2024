import smbus2
import sensors_lib.MyBNO055 as MyBNO055

i2cbus = smbus2.SMBus(1) 
mybno = MyBNO055.BNO055(i2cbus)
mybno.calibration()

