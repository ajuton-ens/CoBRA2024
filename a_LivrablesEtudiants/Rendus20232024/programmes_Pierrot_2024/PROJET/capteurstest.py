import smbus
import time
        
import smbus2
import bme280

bus = smbus.SMBus(1)
address = 0x70

#REQUIRES 5V
def write(value):
        bus.write_byte_data(address, 0, value)
        return -1

def range():
        MSB = bus.read_byte_data(address, 2)
        LSB = bus.read_byte_data(address, 3)
        range = (MSB << 8) + LSB
        return range
    
while True:
        write(0x51)
        time.sleep(0.5)
        rng = range()

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# the sample method will take a single reading and return a
# compensated_reading object
data = bme280.sample(bus, address, calibration_params)

# the compensated_reading class has the following attributes
print(data.id)
print(data.timestamp)
print(data.temperature)
print(data.pressure)
print(data.humidity)

# there is a handy string representation too
print(data)
np = 982.13
altitude = (1-((data.pressure/np)**(1/5.25588)))/(2.25577*10**(-5))
print('altitude =', altitude)