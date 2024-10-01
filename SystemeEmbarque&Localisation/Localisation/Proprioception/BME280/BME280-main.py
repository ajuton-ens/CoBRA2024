from microbit import *
import bme280-library as bme280

i2c.init()
bme = bme280.BME280(i2c=i2c)
print("coucou")
while True:
    print("pression ",bme.pressure)
    pression = bme.read_pressure()/25600.0
    print("pression2 ",pression )
    print(bme.temperature, pression, bme.humidity)
    altitude = 44330.77*(1-(pression/1004.95)**0.19035)
    print(altitude)
    sleep(1000)
