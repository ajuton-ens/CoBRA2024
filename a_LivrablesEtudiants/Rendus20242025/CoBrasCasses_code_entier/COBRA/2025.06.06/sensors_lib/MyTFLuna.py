import smbus

class LidarTFLuna: # pour lire la distance mesurée par le LiDAR TF Luna en utilisant le protocole I2C
    def __init__(self, i2c_address=0x10, i2c_bus=1):
        # Initialiser le bus I2C
        self.address = i2c_address
        self.bus = smbus.SMBus(i2c_bus)
    
    def read_distance(self):
        # Le TF Luna envoie les données de distance en 2 octets
        try:
            # Lire les 2 bytes (octets) de données de distance
            distance_data = self.bus.read_i2c_block_data(self.address, 0x00, 2)  #arguments: adresse unique du périphérique, adresse du premier registre à lire,  nbre de bytes à lire
            # Combiner les 2 octets en une seule valeur de distance en cm
            distance = (distance_data[0] + (distance_data[1] << 8))
            return distance/100
        except Exception as e:
            print(f"Erreur de lecture du LiDAR TF Luna : {e}")
            return None