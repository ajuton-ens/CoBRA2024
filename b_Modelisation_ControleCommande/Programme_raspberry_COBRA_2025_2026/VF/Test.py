from smbus2 import SMBus
import time

class LPS22:
    DEFAULT_ADDRESS = 0x5D

    CTRL_REG1 = 0x10 #addres of CTRL_REG1
    CTRL_REG2 = 0x11 #adress of CTRL_REG2
    RES_CONF_REG = 0x1A #adress of RES_CONF (⚠️ ton code écrasait RES_CONF plus bas)
    PRESS_OUT_XL = 0x28 #adress of the first register of pression

    ODR_RATE = { #rate associate to their binary code
    0:  0b000,  # power-down
    1:  0b001,  # 1 Hz
    10: 0b010,  # 10 Hz
    25: 0b011,  # 25 Hz
    50: 0b100,  # 50 Hz
    75: 0b101,  # 75 Hz
    }

    DEVICE_BANDWIDTH ={ #efficient only if EN_LPFP=1<
    2:  0b00,
    9:  0b10,
    20: 0b11,
    }

    RES_CONF = { 
        "LC":0b1, #Low current mode
        "NM":0b0, #Normal mode
    }

    NOT_ODR_MASK = 0b10001111
    NOT_LPF_MASK= 0b11110011
    BDU_MASK = 0b00000010
    IF_ADD_INC_MASK = 0B00010000
    NOT_FIFO_MASK = 0b10111111
    SWEET_RESET_MASK = 0b00000100
    RES_CONF_MASK = 0b11111110

    def __init__(self, bus, address = DEFAULT_ADDRESS): 
        
        #bus = number of the bus
        #adress = 0x5D if SA0 connect to supply voltage, nothing if not

        self.bus = bus
        self.address = address

        self.p0_hpa = None
        self.z_prev = None

        self.z_filt = None      # altitude filtrée
        self.alpha = 0.05        # coeff filtre exponentiel (0.05 = très stable / 0.3 = plus réactif)

    def read_register (self, reg):   

        #reg = adress of the register you want to read

        return self.bus.read_byte_data(self.address, reg) 
    
    def read_registers(self, start_reg, length):#permit to read numerous registers

        #start_reg = address of te first register you want to read
        #length = number of the register you want to read

        return self.bus.read_i2c_block_data(self.address,start_reg, length)
    
    def write_register (self, reg, data):

        #reg = adress of the register where you want to write
        #data= data that you want to write

        self.bus.write_byte_data(self.address, reg, data & 0xFF)

    def is_LPS_dected(self):

        #Verify if the sensor LPS22 can be detected

        if self.read_register(0x0F) != 0b10110001:
            raise RuntimeError("LPSS2 IS NOT DETECTED") #Message pour Monsieur Juton "est-ce necessaire d'utilsier raise ? est-ce que cela peut causer certains problèmes dans le code? Cette fonction me semble assez puissante"

    def rate_sensor (self, rate_hz:int ):

        #choose the rate between 0,1,10,25,50,75

        if rate_hz not in self.ODR_RATE :
            raise RuntimeError("PLZ GIVE ANOTHER VALUE")
        odr_bits = self.ODR_RATE[rate_hz]
        data = self.read_register(self.CTRL_REG1)
        data &= self.NOT_ODR_MASK #ORD2.1.0 on bit 6.5.4 -> clear ODR bits
        data |= odr_bits<<4 #set new bits wanted
        self.write_register(self.CTRL_REG1, data)

    def low_pass_filter(self, bandwidth: int):

        #bandwidth = n, LPF = ODR/n, for n = 2,9,20

        #note à Monsieur Juton, j'ai lu qu'il fallait mieux séparer les bits "ENABLE" des bits de config, est-ce vraie ? Si oui pourquoi ?

        if bandwidth not in self.DEVICE_BANDWIDTH:
            raise RuntimeError("PLZ USE A BANDWIDTH THAT EXIST") 
        lpf_bits = self.DEVICE_BANDWIDTH[bandwidth]
        data = self.read_register(self.CTRL_REG1)
        data &= self.NOT_LPF_MASK ##EN_LPF AND LPF_CFG cleared
        data |= lpf_bits << 2
        self.write_register(self.CTRL_REG1, data)

    def bdu(self):

        #enable bdu permit to end a measure before begin antoher
        #must have it because of IF_INC_ADD=1

        data = self.read_register(self.CTRL_REG1)
        data |= self.BDU_MASK #BDU have to be enable
        self.write_register(self.CTRL_REG1,data)            
        
    def if_add_inc(self):
        
        #enable if_add_inc to permit to read numerous register for the same measure without a change

        data = self.read_register(self.CTRL_REG2)
        data |= self.IF_ADD_INC_MASK 
        self.write_register(self.CTRL_REG2, data)

    def fifo(self):

        #disable fifo

        data = self.read_register(self.CTRL_REG2)
        data &= self.NOT_FIFO_MASK
        self.write_register(self.CTRL_REG2,data)

    def soft_reset(self):

        #initial state known

        data = self.read_register(self.CTRL_REG2)
        data |= self.SWEET_RESET_MASK
        self.write_register(self.CTRL_REG2, data) 


    #CTRL_REG3 not configurate because interruptions aren't use

    #FIFO_CTRL not configurate beacause not use

    #REF_P_H / REF_P_h not configurate because note use

    def res_conv(self, res_conf):

        #Choose if a low consumption is wanted
        #⚠️ correction: ici tu voulais configurer le registre 0x1A, pas ton dict RES_CONF

        data = self.read_register(self.RES_CONF_REG)
        data &= self.RES_CONF_MASK
        data |= (self.RES_CONF[res_conf] & 0b1) #Low current mode bit
        self.write_register(self.RES_CONF_REG, data)

    #Fifo_STATUS not use

    #STATUS not necessary

    def read_pressure(self):
        pressure_array = self.read_registers(self.PRESS_OUT_XL, 3) #if if_add_inc enable
        pressure = pressure_array[2]<<16 | pressure_array[1] << 8 | pressure_array[0]
        
        if pressure & 0x800000:      # bit 23 = signe
            pressure -= 1 << 24

        pressure_hpa = pressure / 4096.0
        return pressure_hpa
    
    def altitude_from_pressure(self, p_hpa: float, p0_hpa: float):
        # formule barométrique standard (ISA)
        return 44330.0 * (1.0 - (p_hpa / p0_hpa) ** (1.0 / 5.255))
    
    def calibrate_p0(self, duration_s: float = 3.0, rate_hz: int = 25):
        # Calcule p0 comme moyenne sur quelques secondes pour une référence stable
        
        n = max(1, int(duration_s * rate_hz))
        s = 0.0
        
        for _ in range(n):
            s += self.read_pressure()
            time.sleep(1.0 / rate_hz)

        self.p0_hpa = s / n
        self.z_prev = 0.0
        self.z_filt = 0.0
        return self.p0_hpa

    def calcul_z_filtre(self):
        #mesure l'altitude en continu + filtre exponentiel pour réduire le bruit

        p = self.read_pressure()

        if self.p0_hpa is None:
            # si pas calibré, on fait comme avant (mais je recommande calibrate_p0())
            self.p0_hpa = p
            z = 0.0
        else:
            z = self.altitude_from_pressure(p, self.p0_hpa)

        # filtre EMA
        if self.z_filt is None:
            self.z_filt = z
        else:
            self.z_filt = self.alpha * z + (1.0 - self.alpha) * self.z_filt

        return p, z, self.z_filt

        

bus = SMBus(1)           # bus I2C 1 sur Raspberry Pi
sensor = LPS22(bus)

# Détection du capteur
sensor.is_LPS_dected()
print("Capteur détecté")

rate_hz = 25
period = 1/rate_hz

sensor.soft_reset()
time.sleep(0.2)

sensor.if_add_inc()
sensor.bdu()
sensor.fifo()

sensor.rate_sensor(rate_hz)
sensor.low_pass_filter(20)

# Calibrage p0 plus stable (3 secondes)
p0 = sensor.calibrate_p0(duration_s=3.0, rate_hz=rate_hz)
print(f"p0 calibré = {p0:.2f} hPa")

while True:
    p, z, zf = sensor.calcul_z_filtre()
    print(f"P={p:8.2f} hPa | z={z:7.2f} m | z_filt={zf:7.2f} m")
    time.sleep(period)