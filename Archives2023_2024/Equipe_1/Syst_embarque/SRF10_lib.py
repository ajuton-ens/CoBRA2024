import smbus2
import time



class SRF10_i2c():

    def __init__(self, i2c, address = 0x70):
        self.update_height = False
        self.i2c = i2c
        self.address = address
        self.i2c.write_byte_data(self.address, 1, 0x03)
        self.i2c.write_byte_data(self.address, 2, 0x5D)
        self.distances = [0]


    def get_data(self):
        self.i2c.write_byte_data(self.address, 0, 0x52)
        time.sleep(0.07)
        bit1 = self.i2c.read_byte_data(self.address, 2)
        bit2 = self.i2c.read_byte_data(self.address, 3)
        distance = ((bit1 << 8) + bit2)/ (29.4*2)

        if distance < 500:
                self.distances.append(distance)

        moy_derniere_valeurs = sum(self.distances[-min(4,len(self.distances)):])/min(4,len(self.distances))

        if abs(moy_derniere_valeurs - self.distances[-1]) < 5:
                update_height = True
        else : 
            update_height = False

        return round(self.distances[-1],2)
