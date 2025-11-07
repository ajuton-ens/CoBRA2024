class BNO055():
        """ Biliothèque pour l'utilisation de la centrale supelec inertielle BNO055"""
        def __init__(self, bus,i2c_address=0):
                self.address = i2c_address
                self.bus = bus
                print("UNIQUE_ID du BNO055 : ", "FAKE ID")
                #Config en mode fusion

        def calibration(self):
                print("Faire des 8 avec le capteur")
                print("Calibration réussie")
                

        def read_euler(self):
                while True:
                        data = {}
                        data["pitch"]= float(0)
                        data["roll"]= float(0)
                        data["heading"]= float(0)
                        return data
                
        def read_acceleration(self):
                acc = {}
                for i, axis in enumerate(['x', 'y', 'z']):
                        acc[axis] = 0
                return acc

        def read_linear_acceleration(self):
                acc = {}
                for i, axis in enumerate(['x', 'y', 'z']):
                        acc[axis] = 0
                return acc

