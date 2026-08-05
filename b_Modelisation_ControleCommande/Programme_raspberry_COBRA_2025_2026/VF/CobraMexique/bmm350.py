from smbus2 import SMBus
import time
import math

BMM350_ADDR = 0x14

# Registres corrigés
BMM350_REG_CMD = 0x7E
BMM350_REG_PMU_CMD_AGGR_SET = 0x04
BMM350_REG_PMU_CMD = 0x06
BMM350_REG_PMU_CMD_AXIS_EN = 0x05
BMM350_REG_MAG_X_XLSB = 0x31  # Le point de départ des données de mesure

# Valeurs de commandes
BMM350_CMD_SOFTRESET = 0xB6
BMM350_ODR_25_HZ = 0x06
BMM350_AVG_8 = 0x03
BMM350_CMD_NORMAL_MODE = 0x01
BMM350_CMD_UPD_ODR_AVG = 0x02
BMM350_ENABLE_XYZ = 0x07  # Active les 3 axes magnétiques

BMM350_ODR_25_HZ_AVG_8 = BMM350_ODR_25_HZ | (BMM350_AVG_8 << 4)

# Facteurs de conversion d'usine pour le mode 24 bits
BMM350_CONVERSION_COEFFS = [
    0.007069978699505961,
    0.007069978699505961,
    0.007174964082129806,
    0.0009812818524089293,
]

class BMM350:
    def __init__(self, bus, address=BMM350_ADDR):
        self.bus = bus
        self.address = address
        self._init_sensor()

    def _init_sensor(self):
        # 1. Soft Reset
        self.write_register(BMM350_REG_CMD, BMM350_CMD_SOFTRESET)
        time.sleep(0.05)
        
        # 2. Activation des axes
        self.write_register(BMM350_REG_PMU_CMD_AXIS_EN, BMM350_ENABLE_XYZ)
        
        # 3. Paramétrage ODR + Averaging
        self.write_register(BMM350_REG_PMU_CMD_AGGR_SET, BMM350_ODR_25_HZ_AVG_8)
        
        # 4. Envoi de la commande de mise à jour des paramètres
        self.write_register(BMM350_REG_PMU_CMD, BMM350_CMD_UPD_ODR_AVG)
        time.sleep(0.01)
        
        # 5. Passage en mode Normal
        self.write_register(BMM350_REG_PMU_CMD, BMM350_CMD_NORMAL_MODE)
        time.sleep(0.02)

    def write_register(self, reg_addr, data):
        self.bus.write_byte_data(self.address, reg_addr, data)

    def _twos_comp_24(self, val):
        """ Convertit un entier non-signé 24 bits en entier signé """
        if val & (1 << 23):
            val -= (1 << 24)
        return val

    def _read_raw_data(self):
        # On lit 12 octets en bloc : 3 octets par axe (X, Y, Z) + 3 octets pour la Température
        data = self.bus.read_i2c_block_data(self.address, BMM350_REG_MAG_X_XLSB, 12)
        
        # Reconstruction 24 bits (Format Little Endian : XLSB -> LSB -> MSB)
        raw_x = data[0] | (data[1] << 8) | (data[2] << 16)
        raw_y = data[3] | (data[4] << 8) | (data[5] << 16)
        raw_z = data[6] | (data[7] << 8) | (data[8] << 16)
        raw_temp = data[9] | (data[10] << 8) | (data[11] << 16)
        
        # Application du complément à 2
        return (self._twos_comp_24(raw_x), 
                self._twos_comp_24(raw_y), 
                self._twos_comp_24(raw_z), 
                self._twos_comp_24(raw_temp))
    
    def read_mag(self):
        raw_x, raw_y, raw_z, raw_temp = self._read_raw_data()
        
        # Conversion finale en µT (et °C pour la température)
        x = raw_x * BMM350_CONVERSION_COEFFS[0]
        y = raw_y * BMM350_CONVERSION_COEFFS[1]
        z = raw_z * BMM350_CONVERSION_COEFFS[2]
        temp = raw_temp * BMM350_CONVERSION_COEFFS[3]
        
        return x, y, z, temp
    
    def get_cap(self):
        x, y, z, temp = self.read_mag()
        
        # Calcul du cap avec atan2 (Y, X)
        cap = math.atan2(y, x) * (180.0 / math.pi)
        
        # Normalisation indispensable entre 0° et 360° (au lieu du commentaire % 360)
        if cap < 0:
            cap += 360.0
            
        print(f"Cap : {cap:.1f}° | X: {x:.1f} uT | Y: {y:.1f} uT | Z: {z:.1f} uT | T: {temp:.1f}°C")
        return cap

# Boucle principale d'exécution sécurisée
