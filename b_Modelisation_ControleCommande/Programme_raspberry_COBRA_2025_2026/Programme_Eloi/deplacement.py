import cobra_pca9685_v12_COBRAQUAGE as pca9685 #nom du fichier global



class Deplacement:
    def __init__(self, i2cbus):
        

        myPCA9685 = pca9685.PCA9685(i2cbus) # Initialisation du générateur de PWM

        self.brushless = {}
        self.brushless["d"] = pca9685.brushless(myPCA9685,1)
        self.brushless["g"] = pca9685.brushless(myPCA9685,2)
        self.brushless["zg"] = pca9685.brushless(myPCA9685,3)
        self.brushless["av"] = pca9685.brushless(myPCA9685,4)
        self.brushless["ar"] = pca9685.brushless(myPCA9685,5)
        self.brushless["zd"]=pca9685.brushless(myPCA9685,6)

        self.x = 0
        self.y = 0
        self.altitude = 0
        self.lacet = 0
        self.roulis = 0


    def update(self):

        self.roulis = -self.y * 1

        self.brushless["zg"].cmd_vit_pourcent(-self.altitude + self.roulis)
        self.brushless["zd"].cmd_vit_pourcent(-self.altitude - self.roulis)

        self.brushless["g"].cmd_vit_pourcent(self.x)
        self.brushless["d"].cmd_vit_pourcent(-self.x)

        self.brushless["av"].cmd_vit_pourcent(self.lacet + self.y)
        self.brushless["ar"].cmd_vit_pourcent(self.lacet - self.y)



    def setAltitude(self, v):
        self.altitude = min(max(v, -100), 100)
        self.update()

    def setAngle(self, v):
        self.lacet = min(max(v, -100), 100)
        self.update()

    def setX(self, v):
        self.x = min(max(v, -100), 100)
        self.update()

    def setY(self, v):
        self.y = min(max(v, -100), 100)
        self.update()

    def setRoulis(self, v):
        self.roulis = min(max(v, -100), 100)
        self.update()


    def zeros(self):
        self.x = 0
        self.y = 0
        self.altitude = 0
        self.lacet = 0
        self.roulis = 0
        self.update()