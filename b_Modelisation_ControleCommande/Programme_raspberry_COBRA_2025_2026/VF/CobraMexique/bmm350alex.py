from smbus2 import SMBus
import time
import math
import numpy as np


class BMM35() :



    DEFAULT_ADDRESS = 0x14
    DUMMY = 2 # il y a deux octets à ignorer 
    # ----------------------------------------------------------------
    # Registres de statut et identification
    # ----------------------------------------------------------------
    CHIP_ID             = 0x00  # adresse du registre CHIP_ID (doit valoir 0x33)

    # ----------------------------------------------------------------
    # Registres de configuration PMU
    # ----------------------------------------------------------------
    PMU_CMD_AGGR_SET    = 0x04  # adresse du registre ODR et AVG
    PMU_CMD_AXIS_EN     = 0x05  # adresse du registre d'activation des axes X Y Z
    PMU_CMD             = 0x06  # adresse du registre de commande de mode
    PMU_CMD_STATUS_0    = 0x07  # adresse du registre d'état PMU (busy, mode normal)

    # ----------------------------------------------------------------
    # Registres d'interruption
    # ----------------------------------------------------------------
    INT_CTRL            = 0x2E  # adresse du registre de configuration interruption
    INT_STATUS          = 0x30  # adresse du registre statut interruption (bit5 = DRDY)

    # ----------------------------------------------------------------
    # Registres de données champ X (burst read depuis 0x31)
    # ----------------------------------------------------------------
    MAG_X_XLSB          = 0x31  # adresse du premier registre de données champ X bits 7:0

    # ----------------------------------------------------------------
    # Registres OTP (coefficients de compensation)
    # ----------------------------------------------------------------
    OTP_CMD_REG         = 0x50  # adresse du registre commande OTP
    OTP_DATA_MSB        = 0x52  # adresse du registre donnée OTP octet fort
    OTP_DATA_LSB        = 0x53  # adresse du registre donnée OTP octet faible
    OTP_STATUS          = 0x55  # adresse du registre statut OTP (bit0 = commande terminée)

    # ----------------------------------------------------------------
    # Registre de commande générale
    # ----------------------------------------------------------------
    CMD                 = 0x7E  # adresse du registre de commande générale (soft reset)

    # ----------------------------------------------------------------
    # Adresses des mots OTP (coefficients de compensation d'usine)
    # ----------------------------------------------------------------
    OTP_TEMP_OFF_SENS = 0x0D
    OTP_OFF_XY        = 0x0E
    OTP_OFF_YZ        = 0x0F
    OTP_OFF_Z_TSENSX  = 0x10
    OTP_TSENSY_Z      = 0x11
    OTP_SENS_X_TCO_X  = 0x12
    OTP_SENS_Y_TCO_Y  = 0x13
    OTP_SENS_Z_TCO_Z  = 0x14
    OTP_DUT_T0        = 0x18


    #DICTIONNAIRES

    ODR_RATE = {  # fréquence associée à son code binaire
        "ODR_400HZ"    : 0b00000010,
        "ODR_200HZ"    : 0b00000011,
        "ODR_100HZ"    : 0b00000100,
        "ODR_50HZ"     : 0b00000101,
        "ODR_25HZ"     : 0b00000110,
        "ODR_12_5HZ"   : 0b00000111,
        "ODR_6_25HZ"   : 0b00001000,
        "ODR_3_125HZ"  : 0b00001001,
        "ODR_1_5625HZ" : 0b00001010,
    }

    AVG_SAMPLES = {  # nombre d'échantillons moyennés associé à son code binaire
        1     : 0b00000000,  # 1 échantillon  - Low Power       (~120 µA)
        2     : 0b00010000,  # 2 échantillons - Regular Power   (~190 µA) ← par défaut
        4     : 0b00100000,  # 4 échantillons - Low Noise       (~335 µA)
        8     : 0b00110000,  # 8 échantillons - Ultra Low Noise
    }

    AXIS_EN = {
        "X"   : 0b00000001,  # axe X seulement
        "Y"   : 0b00000010,  # axe Y seulement
        "Z"   : 0b00000100,  # axe Z seulement
        "XY"  : 0b00000011,  # axes X et Y
        "XZ"  : 0b00000101,  # axes X et Z
        "YZ"  : 0b00000110,  # axes Y et Z
        "XYZ" : 0b00000111,  # tous les axes ← par défaut
    }

    PMU_CMDS = {
        "SUSPEND"  : 0x00,  # dort - consommation minimale (1.8 µA)
        "NORMAL"   : 0x01,  # mesures continues au rythme ODR
        "UPD_OAE"  : 0x02,  # applique la nouvelle config ODR/AVG
    }


    #MASQUES
    NOT_ODR_MASK = 0b11110000  # garde les bits AVG, efface les bits ODR
    NOT_AVG_MASK = 0b00001111  # garde les bits OVR, efface les bits AVG

    def __init__(self, bus, address=DEFAULT_ADDRESS):
        self.bus     = bus
        self.address = address

        # coefficients OTP - remplis par _load_otp_coefficients()
        self.off_x     = 0.0
        self.off_y     = 0.0
        self.off_z     = 0.0
        self.sens_x    = 0.0
        self.sens_y    = 0.0
        self.sens_z    = 0.0
        self.tco_x     = 0.0
        self.tco_y     = 0.0
        self.tco_z     = 0.0
        self.tcs_x     = 0.0
        self.tcs_y     = 0.0
        self.tcs_z     = 0.0
        self.t0        = 25.0
        self.temp_sens = 0.0
        self.temp_off  = 0.0

    def read_register(self, reg):
        data = self.bus.read_i2c_block_data(self.address, reg, self.DUMMY + 1)
        return data[self.DUMMY]

    def write_register(self, reg, data):
        self.bus.write_byte_data(self.address, reg, data & 0xFF)

    def is_BMM50_detected(self):
        if self.read_register(self.CHIP_ID) != 0x33:
            raise RuntimeError("BMM350 IS NOT DETECTED")

    def rate_sensor(self, rate_hz):
        if rate_hz not in self.ODR_RATE:
            raise RuntimeError("PLZ GIVE ANOTHER VALUE OF RATE")
        odr_bits = self.ODR_RATE[rate_hz]
        data = self.read_register(self.PMU_CMD_AGGR_SET)
        data = (data & self.NOT_ODR_MASK) | odr_bits
        self.write_register(self.PMU_CMD_AGGR_SET, data)
        self.write_register(self.PMU_CMD, self.PMU_CMDS["UPD_OAE"])
        self.wait_pmu_ready()

    def avg_sensor(self, avg):
        if avg not in self.AVG_SAMPLES:
            raise RuntimeError("PLZ GIVE ANOTHER VALUE OF AVG")
        avg_bits = self.AVG_SAMPLES[avg]
        data = self.read_register(self.PMU_CMD_AGGR_SET)
        data = (data & self.NOT_AVG_MASK) | avg_bits
        self.write_register(self.PMU_CMD_AGGR_SET, data)
        self.write_register(self.PMU_CMD, self.PMU_CMDS["UPD_OAE"])
        self.wait_pmu_ready()

    def set_axes(self, axes):
        if axes not in self.AXIS_EN:
            raise RuntimeError("Axe non valide, choisir X,Y,Z,XY,XZ,YZ,XYZ")
        self.write_register(self.PMU_CMD, 0x00)
        time.sleep(0.001)
        self.write_register(self.PMU_CMD_AXIS_EN, self.AXIS_EN[axes])

    def set_suspend(self):
        self.write_register(self.PMU_CMD, self.PMU_CMDS["SUSPEND"])
        self.wait_pmu_ready()

    def set_normal_mode(self):
        self.write_register(self.PMU_CMD, self.PMU_CMDS["NORMAL"])
        time.sleep(0.080)            # sleep obligatoire
        self.wait_pmu_ready()

    def wait_pmu_ready(self, timeout=100):

        # attend que le PMU ait fini sa commande
        # timeout = nombre maximum de tentatives (100ms max)
        #remplace les sleep entre mesure pour être sur qu'on puisse faire une mesure

        for _ in range(timeout):
            status = self.read_register(self.PMU_CMD_STATUS_0)
            if not (status & 0b00000001):
                return True       # test si PMU libre
            time.sleep(0.001)     # attendre 1ms et réessayer
        raise RuntimeError("PMU still busy after timeout")

    def soft_reset(self):
        # remet le capteur dans son état initial
        # à appeler systématiquement au début de init()
        self.write_register(self.CMD, 0xB6)  # déclenche le reset
        time.sleep(0.002)                    # attendre 2ms
        self.write_register(self.CMD, 0x00)  # confirme la fin du reset
        time.sleep(0.002)                    # attendre 2ms

    def _read_otp_word(self, word_addr):
        #lecture des coefficients d'usine
        cmd = 0x80 # 0x20| (word_addr & 0x1F)
        self.write_register(self.OTP_CMD_REG, cmd)
        for _ in range(20):
            status = self.read_register(self.OTP_STATUS)
            if status & 0x01:
                break              # commande terminée on peut lire
            time.sleep(0.001)
        msb = self.read_register(self.OTP_DATA_MSB)   # octet fort
        lsb = self.read_register(self.OTP_DATA_LSB)   # octet faible
        return (msb << 8) | lsb

    def _sign_extend(self, value, bits):
        # convertit un entier non signé en signé
        sign_bit = 1 << (bits - 1)
        return (value & (sign_bit - 1)) - (value & sign_bit)


    def _load_otp_coefficients(self):
        # charge les coefficients de compensation gravés en usine

        # température
        w0D = self._read_otp_word(self.OTP_TEMP_OFF_SENS)
        self.temp_off  = self._sign_extend(w0D & 0x01FF, 9) / 2.0
        self.temp_sens = self._sign_extend((w0D >> 9) & 0x7F, 7) / 2000.0

        # offsets magnétiques
        w0E = self._read_otp_word(self.OTP_OFF_XY)
        w0F = self._read_otp_word(self.OTP_OFF_YZ)
        w10 = self._read_otp_word(self.OTP_OFF_Z_TSENSX)
        self.off_x = self._sign_extend((w0E >> 8) & 0xFF, 8) * 2.0
        self.off_y = self._sign_extend(w0F >> 8, 8) * 2.0
        self.off_z = self._sign_extend(w0F & 0xFF, 8) * 2.0

        # gains et coefficients température
        w11 = self._read_otp_word(self.OTP_TSENSY_Z)
        w12 = self._read_otp_word(self.OTP_SENS_X_TCO_X)
        w13 = self._read_otp_word(self.OTP_SENS_Y_TCO_Y)
        w14 = self._read_otp_word(self.OTP_SENS_Z_TCO_Z)
        self.sens_x = self._sign_extend((w12 >> 8) & 0xFF, 8) / 256.0
        self.sens_y = self._sign_extend((w13 >> 8) & 0xFF, 8) / 256.0
        self.sens_z = self._sign_extend((w14 >> 8) & 0xFF, 8) / 256.0
        self.tco_x  = self._sign_extend(w12 & 0xFF, 8) / 32.0
        self.tco_y  = self._sign_extend(w13 & 0xFF, 8) / 32.0
        self.tco_z  = self._sign_extend(w14 & 0xFF, 8) / 32.0
        self.tcs_x  = self._sign_extend(w10 & 0xFF, 8) / 16384.0
        self.tcs_y  = self._sign_extend((w11 >> 8) & 0xFF, 8) / 16384.0
        self.tcs_z  = self._sign_extend(w11 & 0xFF, 8) / 16384.0

        # température de référence
        w18 = self._read_otp_word(self.OTP_DUT_T0)
        self.t0 = self._sign_extend(w18, 16) / 512.0


    def init(self):
        self.soft_reset()
        time.sleep(0.100)
        self.is_BMM50_detected()
        self._load_otp_coefficients()
        self.write_register(self.OTP_CMD_REG, 0x80)  # fermer l'accès OTP
        time.sleep(0.002)
        self.rate_sensor("ODR_100HZ")
        self.avg_sensor(2)
        self.set_axes("XYZ")
        self.write_register(self.INT_CTRL, 0b10000000)  # activation DRDY


    def burst_read(self, reg_start, length):
        # lit plusieurs registres d'un coup - obligatoire pour les données mag
        data = self.bus.read_i2c_block_data(self.address, reg_start, length + self.DUMMY)
        return data[self.DUMMY:]


    def _to_signed_21bit(self, xlsb, lsb, msb):
        # assemble 3 octets en entier signé 21 bits
        raw = (msb << 16) | (lsb << 8) | xlsb
        raw = raw & 0x1FFFFF
        if raw & 0x100000:
            raw -= 0x200000
        return raw


    def _read_raw_data(self):
        regs     = self.burst_read(self.MAG_X_XLSB, 15)
        raw_x    = self._to_signed_21bit(regs[0],  regs[1],  regs[2])
        raw_y    = self._to_signed_21bit(regs[3],  regs[4],  regs[5])
        raw_z    = self._to_signed_21bit(regs[6],  regs[7],  regs[8])
        raw_temp = self._to_signed_21bit(regs[9],  regs[10], regs[11])
        return raw_x, raw_y, raw_z, raw_temp


    def _compensate(self, raw_x, raw_y, raw_z, raw_temp):
        # applique les corrections offset + gain + température
        lsb_to_ut = 1.0 / (1 << 14)
        temp    = (raw_temp * lsb_to_ut) * (1.0 + self.temp_sens) + self.temp_off
        delta_t = temp - self.t0
        hx = (raw_x * lsb_to_ut) * (1.0 + self.sens_x + self.tcs_x * delta_t) + self.off_x + self.tco_x * delta_t
        hy = (raw_y * lsb_to_ut) * (1.0 + self.sens_y + self.tcs_y * delta_t) + self.off_y + self.tco_y * delta_t
        hz = (raw_z * lsb_to_ut) * (1.0 + self.sens_z + self.tcs_z * delta_t) + self.off_z + self.tco_z * delta_t
        return hx, hy, hz, temp


    def data_ready(self):
        return bool(self.read_register(self.INT_STATUS) & 0b00000100)


    def wait_data_ready(self, timeout=200):
        for _ in range(timeout):
            if self.data_ready():
                return True
            time.sleep(0.002)
        raise RuntimeError("Data not ready after timeout")


    def read_mag(self):
        # retourne (x, y, z, temperature) en µT et °C
        self.wait_data_ready()
        raw_x, raw_y, raw_z, raw_temp = self._read_raw_data()
        return self._compensate(raw_x, raw_y, raw_z, raw_temp)

    def get_cap(self):
        # retourne le cap magnétique en degrés (0° = Nord, 90° = Est)
        # à appeler depuis le code de fusion avec l'accéléromètre de Virgile
        x, y, z, temp = self.read_mag()
        cap = 180/np.pi *math.atan2(y, x) #% 360
        print(f"Cap magnétique : {cap:.2f}, {x}, {y}, {z}°")
        return cap
    
    def get_xyz(self):
        x,y,z,temp=self.read_mag()
        return x,y,z