from smbus2 import SMBus  
import time
import numpy as np

class IMU:
    #Accéléromètre
    # BMI088 register addresses

    BMI088_ACC_CHIP_ID     = 0x00 # Accelerometer chip ID

    BMI088_ACC_CONF      = 0x40
    BMI088_ACC_RANGE     = 0x41
    BMI088_ACC_PWR_CONF  = 0x7C
    BMI088_ACC_PWR_CTRL  = 0x7D
    BMI088_ACC_SOFTRESET = 0x7E
    BMI088_ACC_X_LSB     = 0x12
    BMI088_ACC_X_MSB     = 0x13
    BMI088_ACC_Y_LSB     = 0x14
    BMI088_ACC_Y_MSB     = 0x15
    BMI088_ACC_Z_LSB     = 0x16
    BMI088_ACC_Z_MSB     = 0x17
    BMI088_ACC_TEMP_MSB  = 0x22
    BMI088_ACC_TEMP_LSB  = 0x23
    

    # Essential registers for basic functionality
    BMI088_ACC_STATUS    = 0x1D        # Accelerometer status register
    BMI088_ACC_SELF_TEST = 0x6D      # Accelerometer self-test register
 
   
    # Power management registers
    BMI088_ACC_PWR_CTRL_ACC_ENABLE = 0x04  # Enable accelerometer
    #######################################################################################################
    
    # Device addresses
    BMI088_ACC_ADDR = 0x19  # Accelerometer I2C address
    

    # Configuration values
    BMI088_ACC_RANGE_3G  = 0x00
    BMI088_ACC_RANGE_6G  = 0x01
    BMI088_ACC_RANGE_12G = 0x02
    BMI088_ACC_RANGE_24G = 0x03

    BMI088_GYR_RANGE_2000DPS = 0x00
    BMI088_GYR_RANGE_1000DPS = 0x01
    BMI088_GYR_RANGE_500DPS  = 0x02
    BMI088_GYR_RANGE_250DPS  = 0x03
    BMI088_GYR_RANGE_125DPS  = 0x04

    # Data rate values
    BMI088_ACC_ODR_12HZ   = 0x05
    BMI088_ACC_ODR_25HZ   = 0x06
    BMI088_ACC_ODR_50HZ   = 0x07
    BMI088_ACC_ODR_100HZ  = 0x08
    BMI088_ACC_ODR_200HZ  = 0x09
    BMI088_ACC_ODR_400HZ  = 0x0A
    BMI088_ACC_ODR_800HZ  = 0x0B
    BMI088_ACC_ODR_1600HZ = 0x0C

    

    # Error codes
    BMI088_OK          =  0
    BMI088_ERR_NULL    = -1
    BMI088_ERR_BUS     = -2
    BMI088_ERR_INVALID = -3
    BMI088_ERR_TIMEOUT = -4

    plage_accel = BMI088_ACC_RANGE_3G
    plage_gyro  = BMI088_GYR_RANGE_125DPS

    #========================================================
    #Partie Gyro
    #========================================================
    BMI088_GYR_ADDR = 0x69  # Gyroscope I2C address
    

    BMI088_GYR_CHIP_ID     = 0x00 # Gyroscope chip ID
    BMI088_GYR_RANGE     = 0x0F
    BMI088_GYR_BANDWIDTH        = 0x10
    BMI088_GYR_LPM1      = 0x11
    BMI088_GYR_SOFTRESET = 0x14
    BMI088_GYR_CTRL      = 0x15
    BMI088_GYR_X_LSB     = 0x02
    BMI088_GYR_X_MSB     = 0x03
    BMI088_GYR_Y_LSB     = 0x04
    BMI088_GYR_Y_MSB     = 0x05
    BMI088_GYR_Z_LSB     = 0x06
    BMI088_GYR_Z_MSB     = 0x07
    BMI088_GYR_SELF_TEST = 0x3C

    BMI088_GYR_ODR_2000HZ_FC532 = 0x00
    BMI088_GYR_ODR_2000HZ_FC230 = 0x01
    BMI088_GYR_ODR_1000HZ_FC116 = 0x02
    BMI088_GYR_ODR_400HZ_FC47  = 0x03
    BMI088_GYR_ODR_200HZ_FC23  = 0x04
    BMI088_GYR_ODR_100HZ_FC12  = 0x05
    BMI088_GYR_ODR_200HZ_FC64  = 0x06
    BMI088_GYR_ODR_100HZ_FC32  = 0x07



    def __init__(self, bus):
        self.i2cbus = bus

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #définition des fonctions de base 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def lire(self, Capt, registre): #Capt est l'adresse I2C du capteur
        return self.i2cbus.read_byte_data(Capt, registre)
    def lireNbytes(self, Capt, registre,Nbytes): #Capt est l'adresse I2C du capteur
        return self.i2cbus.read_block_data(Capt,registre,Nbytes) 
    def ecrire(self, Capt, registre, contenu):
        return self.i2cbus.write_byte_data(Capt, registre, contenu)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #allumage du capteur
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def allumage_accel(self):
        self.ecrire(self.BMI088_ACC_ADDR, 0x7D, 0x04)
    #le gyroscope est allumé par défaut

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #initialisation Accel
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def init_accel(self):
        self.ecrire(self.BMI088_ACC_ADDR, self.BMI088_ACC_RANGE, self.plage_accel)#plage d'accélération à +-3g
        #ODR à 50 Hz et -3DB à 5Hz
        #voir paragraphe 4.4.1 ici, 10HZ de fréquence de coupure et 100Hz d'échantillonnage
        self.ecrire(self.BMI088_ACC_ADDR, self.BMI088_ACC_CONF, 0X88)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #lecture Accel
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    def accxyz(self):
#        tab = self.lireNbytes(self.BMI088_ACC_ADDR, self.BMI088_ACC_X_LSB,6)
#        print(tab)
#        accxMSB = tab[1]
#        accxLSB = tab[0]
#        accyMSB = tab[3]
#        accyLSB = tab[2]
#        acczMSB = tab[5]
#        acczLSB = tab[6]
#
#        ACCint16 = 256*accxMSB + accxLSB
#        if ACCint16>32767 :
#            accx=(ACCint16-65536)*1000.0*2**(1+self.plage_accel)*1.5/32768
#        else:
#            accx=ACCint16*1000.0*2**(1+self.plage_accel)*1.5/32768
#
#        ACCint16 = 256*accyMSB + accyLSB
#        if ACCint16>32767 :
#            accy=(ACCint16-65536)*1000.0*2**(1+self.plage_accel)*1.5/32768
#        else:
#            accy=ACCint16*1000.0*2**(1+self.plage_accel)*1.5/32768
#
#        ACCint16 = 256*acczMSB + acczLSB
#        if ACCint16>32767 :
#            accz=(ACCint16-65536)*1000.0*2**(1+self.plage_accel)*1.5/32768
#        else:
#            accz=ACCint16*1000.0*2**(1+self.plage_accel)*1.5/32768
#        return accx*9,81/1000, accy*9.81/1000, accz*9.81/1000 #renvoie les accélérations en m.s^-3


    def accx(self):
        accxLSB = self.lire(self.BMI088_ACC_ADDR, self.BMI088_ACC_X_LSB)
        accxMSB = self.lire(self.BMI088_ACC_ADDR, self.BMI088_ACC_X_MSB)
        ACCint16 = 256*accxMSB + accxLSB
        if ACCint16>32767 :
            return (ACCint16-65536)*1000.0*2**(1+self.plage_accel)*1.5/32768
        else:
            return ACCint16*1000.0*2**(1+self.plage_accel)*1.5/32768

    def accy(self):
        accyLSB = self.lire(self.BMI088_ACC_ADDR, self.BMI088_ACC_Y_LSB)
        accyMSB = self.lire(self.BMI088_ACC_ADDR, self.BMI088_ACC_Y_MSB)
        ACCint16 = 256*accyMSB + accyLSB
        if ACCint16>32767 :
            return (ACCint16-65536)*1000.0*2**(1+self.plage_accel)*1.5/32768
        else:
            return ACCint16*1000.0*2**(1+self.plage_accel)*1.5/32768

    def accz(self):
        acczLSB = self.lire(self.BMI088_ACC_ADDR, self.BMI088_ACC_Z_LSB)
        acczMSB = self.lire(self.BMI088_ACC_ADDR, self.BMI088_ACC_Z_MSB)
        ACCint16 = 256*acczMSB + acczLSB
        if ACCint16>32767 :
            return (ACCint16-65536)*1000.0*2**(1+self.plage_accel)*1.5/32768
        else:
            return ACCint16*1000.0*2**(1+self.plage_accel)*1.5/32768

    def accxyz(self):
        ax=self.accx()*9.81/1000
        ay=self.accy()*9.81/1000
        az=self.accz()*9.81/1000
        return ax,ay,az

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #initialisation Gyro
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    plage_giropm=500 # à changer si modification de la plage du gyroscope
    def init_gyro(self):
        self.ecrire(self.BMI088_GYR_ADDR, self.BMI088_GYR_RANGE, self.BMI088_GYR_RANGE_500DPS)#plage du gyroscope à +-500dps
        self.ecrire(self.BMI088_GYR_ADDR, self.BMI088_GYR_BANDWIDTH, self.BMI088_GYR_ODR_100HZ_FC12)#ODR à 100 Hz

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #lecture Gyro
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    def gyrxyz(self):
#        tab = self.lireNbytes(self.BMI088_ACC_ADDR, self.BMI088_GYR_X_LSB,6)
#        print(tab)
#        gyrxMSB = tab[1]
#        gyrxLSB = tab[0]
#        gyryMSB = tab[3]
#        gyryLSB = tab[2]
#        gyrzMSB = tab[5]
#        gyrzLSB = tab[6]
#
#        GYRint16 = 256*gyrxMSB + gyrxLSB
#        if GYRint16>32767 :
#            gyrx=(GYRint16-65536)/32627*2000
#        else:
#            gyrx=GYRint16/32627*2000
#
#        GYRint16 = 256*gyryMSB + gyryLSB
#        if GYRint16>32767 :
#            gyry=(GYRint16-65536)/32627*2000
#        else:
#            gyry=GYRint16/32627*2000
#
#        GYRint16 = 256*gyrzMSB + gyrzLSB
#        if GYRint16>32767 :
#            gyrz=(GYRint16-65536)/32627*2000
#        else:
#            gyrz=GYRint16/32627*2000
#        return gyrx, gyry, gyrz #renvoie les vitesses angulaires den dps


    def gyrox(self):
        gyroxLSB = self.lire(self.BMI088_GYR_ADDR, self.BMI088_GYR_X_LSB)
        gyroxMSB = self.lire(self.BMI088_GYR_ADDR, self.BMI088_GYR_X_MSB)
        GYROint16 = 256*gyroxMSB + gyroxLSB
        if GYROint16>32767 :
            return (GYROint16-65536)/32767*self.plage_giropm
        else:
            return GYROint16/32767*self.plage_giropm #renvoie la valeur en dps
        

    def gyroy(self):
        gyroyLSB = self.lire(self.BMI088_GYR_ADDR, self.BMI088_GYR_Y_LSB)
        gyroyMSB = self.lire(self.BMI088_GYR_ADDR, self.BMI088_GYR_Y_MSB)
        GYROint16 = 256*gyroyMSB + gyroyLSB
        if GYROint16>32767 :
            return (GYROint16-65536)/32767*self.plage_giropm
        else:
            return GYROint16/32767*self.plage_giropm #renvoie la valeur en dps

    def gyroz(self):
        gyrozLSB = self.lire(self.BMI088_GYR_ADDR, self.BMI088_GYR_Z_LSB)
        gyrozMSB = self.lire(self.BMI088_GYR_ADDR, self.BMI088_GYR_Z_MSB)
        GYROint16 = 256*gyrozMSB + gyrozLSB
        if GYROint16>32767 :
            return (GYROint16-65536)/32767*self.plage_giropm
        else:
            return GYROint16/32767*self.plage_giropm #renvoie la valeur en dps

    def gyrxyz(self):
        gx=self.gyrox()
        gy=self.gyroy()
        gz=self.gyroz()
        return gx*np.pi/180, gy*np.pi/180, gz*np.pi/180 #renvoie les vitesses angulaires en rad/s

    def Rotation(self,Phi , Theta, Psi):
        MatR= [[np.cos(Psi)*np.cos(Theta), np.cos(Theta)*np.sin(Psi), -np.sin(Theta)],
               [np.cos(Psi)*np.sin(Theta)*np.sin(Phi)-np.cos(Phi)*np.sin(Psi), np.cos(Psi)*np.cos(Phi)+np.sin(Psi)*np.sin(Theta)*np.sin(Phi), np.cos(Theta)*np.sin(Phi)],
               [np.cos(Psi)*np.sin(Theta)*np.cos(Phi)+np.sin(Psi)*np.sin(Phi), np.cos(Phi)*np.sin(Psi)*np.sin(Theta)-np.cos(Psi)*np.sin(Phi), np.cos(Theta)*np.cos(Phi)]]
        return np.array(MatR)

    def passe_bas (self,K, Te, Tau, S_1,E,E_1):
        return (1/(1+2*Tau/Te))*(K*E+K*E_1-(1-2*Tau/Te)*S_1)