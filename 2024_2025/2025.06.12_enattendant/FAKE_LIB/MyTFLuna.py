class LidarTFLuna: # pour lire la distance mesurée par le LiDAR TF Luna en utilisant le protocole I2C
    def __init__(self, i2c_address=0x10, i2c_bus=1):
        self.address = i2c_address
        self.bus = 0
    
    def read_distance(self):
        return 0
