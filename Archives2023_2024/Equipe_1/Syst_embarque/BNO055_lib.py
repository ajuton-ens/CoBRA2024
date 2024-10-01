import time
import struct

_CHIP_ID =  0xA0

CONFIG_MODE =  0x00
ACCONLY_MODE =  0x01
MAGONLY_MODE =  0x02
GYRONLY_MODE =  0x03
ACCMAG_MODE =  0x04
ACCGYRO_MODE =  0x05
MAGGYRO_MODE =  0x06
AMG_MODE =  0x07
IMUPLUS_MODE =  0x08
COMPASS_MODE =  0x09
M4G_MODE =  0x0A
NDOF_FMC_OFF_MODE =  0x0B
NDOF_MODE =  0x0C

ACCEL_2G =  0x00  # For accel_range property
ACCEL_4G =  0x01  # Default
ACCEL_8G =  0x02
ACCEL_16G =  0x03
ACCEL_7_81HZ =  0x00  # For accel_bandwidth property
ACCEL_15_63HZ =  0x04
ACCEL_31_25HZ =  0x08
ACCEL_62_5HZ =  0x0C  # Default
ACCEL_125HZ =  0x10
ACCEL_250HZ =  0x14
ACCEL_500HZ =  0x18
ACCEL_1000HZ =  0x1C
ACCEL_NORMAL_MODE =  0x00 # Default. For accel_mode property
ACCEL_SUSPEND_MODE =  0x20
ACCEL_LOWPOWER1_MODE =  0x40
ACCEL_STANDBY_MODE =  0x60
ACCEL_LOWPOWER2_MODE =  0x80
ACCEL_DEEPSUSPEND_MODE =  0xA0

GYRO_2000_DPS =  0x00  # Default. For gyro_range property
GYRO_1000_DPS =  0x01
GYRO_500_DPS =  0x02
GYRO_250_DPS =  0x03
GYRO_125_DPS =  0x04
GYRO_523HZ =  0x00  # For gyro_bandwidth property
GYRO_230HZ =  0x08
GYRO_116HZ =  0x10
GYRO_47HZ =  0x18
GYRO_23HZ =  0x20
GYRO_12HZ =  0x28
GYRO_64HZ =  0x30
GYRO_32HZ =  0x38 # Default
GYRO_NORMAL_MODE =  0x00 # Default. For gyro_mode property
GYRO_FASTPOWERUP_MODE =  0x01
GYRO_DEEPSUSPEND_MODE =  0x02
GYRO_SUSPEND_MODE =  0x03
GYRO_ADVANCEDPOWERSAVE_MODE =  0x04

MAGNET_2HZ =  0x00  # For magnet_rate property
MAGNET_6HZ =  0x01
MAGNET_8HZ =  0x02
MAGNET_10HZ =  0x03
MAGNET_15HZ =  0x04
MAGNET_20HZ =  0x05  # Default
MAGNET_25HZ =  0x06
MAGNET_30HZ =  0x07
MAGNET_LOWPOWER_MODE =  0x00 # For magnet_operation_mode property
MAGNET_REGULAR_MODE =  0x08 # Default
MAGNET_ENHANCEDREGULAR_MODE =  0x10
MAGNET_ACCURACY_MODE =  0x18
MAGNET_NORMAL_MODE =  0x00 # for magnet_power_mode property
MAGNET_SLEEP_MODE =  0x20
MAGNET_SUSPEND_MODE =  0x40
MAGNET_FORCEMODE_MODE =  0x60  # Default

_POWER_NORMAL =  0x00
_POWER_LOW =  0x01
_POWER_SUSPEND =  0x02

_MODE_REGISTER =  0x3D
_PAGE_REGISTER =  0x07
_ACCEL_CONFIG_REGISTER =  0x08
_MAGNET_CONFIG_REGISTER =  0x09
_GYRO_CONFIG_0_REGISTER =  0x0A
_GYRO_CONFIG_1_REGISTER =  0x0B
_CALIBRATION_REGISTER =  0x35
_OFFSET_ACCEL_REGISTER =  0x55
_OFFSET_MAGNET_REGISTER =  0x5B
_OFFSET_GYRO_REGISTER =  0x61
_RADIUS_ACCEL_REGISTER =  0x67
_RADIUS_MAGNET_REGISTER =  0x69
_TRIGGER_REGISTER =  0x3F
_POWER_REGISTER =  0x3E
_ID_REGISTER =  0x00
# Axis remap registers and values
_AXIS_MAP_CONFIG_REGISTER =  0x41
_AXIS_MAP_SIGN_REGISTER =  0x42
AXIS_REMAP_X =  0x00
AXIS_REMAP_Y =  0x01
AXIS_REMAP_Z =  0x02
AXIS_REMAP_POSITIVE =  0x00
AXIS_REMAP_NEGATIVE =  0x01




class BNO055_i2c():

    def __init__(self, i2c, adress = 0x28):

        self.i2c = i2c
        self.address = adress
        
        self.reset()
        self.i2c.write_byte_data(self.address,_POWER_REGISTER,0x00)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        self.i2c.write_byte_data(self.address,_TRIGGER_REGISTER, 0x00)
        self.accel_range = ACCEL_4G
        self.gyro_range = GYRO_2000_DPS
        self.magnet_rate = MAGNET_20HZ
        time.sleep(0.01)
        self.mode = NDOF_MODE
        time.sleep(0.01)



    def reset(self):
        """Resets the sensor to default settings."""
        self.mode = CONFIG_MODE
        self.i2c.write_byte_data(self.address,_TRIGGER_REGISTER, 0x20)
        time.sleep(0.7)

    @property
    def mode(self):
        return self.i2c.read_byte_data(self.address,_MODE_REGISTER) & 0b00001111  # Datasheet Table 4-2

    @mode.setter
    def mode(self, new_mode: int):
        self.i2c.write_byte_data(self.address,_MODE_REGISTER, CONFIG_MODE)  # Empirically necessary
        time.sleep(0.02)  # Datasheet table 3.6
        if new_mode != CONFIG_MODE:
            self.i2c.write_byte_data(self.address,_MODE_REGISTER, new_mode)
            time.sleep(0.01)  # Table 3.6


    @property
    def temperature(self):
        return self.i2c.read_byte_data(self.address,0x34)

    @property
    def acceleration(self):
        """Gives the raw accelerometer readings, in m/s.
        Returns an empty tuple of length 3 when this property has been disabled by the current mode.
        """
        if self.mode not in [0x00, 0x02, 0x03, 0x06]:
            Register = self.i2c.read_i2c_block_data(self.address, 0x08, 6)
            ax = struct.unpack('h',bytes([Register[0],Register[1]]))[0]
            ay = struct.unpack('h',bytes([Register[2],Register[3]]))[0]
            az = struct.unpack('h',bytes([Register[4],Register[5]]))[0]
            return [ax/100,ay/100,az/100]
        return (None, None, None)

    @property
    def magnetic(self):
        """Gives the raw magnetometer readings in microteslas.
        Returns an empty tuple of length 3 when this property has been disabled by the current mode.
        """
        if self.mode not in [0x00, 0x01, 0x03, 0x05, 0x08]:
            Register = self.i2c.read_i2c_block_data(self.address, 0x0E, 6)
            mx = struct.unpack('h',bytes([Register[0],Register[1]]))[0]
            my = struct.unpack('h',bytes([Register[2],Register[3]]))[0]
            mz = struct.unpack('h',bytes([Register[4],Register[5]]))[0]
            return [mx/ 16 ,my/ 16 ,mz/ 16 ]
        return (None, None, None)

    @property
    def gyro(self):
        """Gives the raw gyroscope reading in radians per second.
        Returns an empty tuple of length 3 when this property has been disabled by the current mode.
        """
        if self.mode not in [0x00, 0x01, 0x02, 0x04, 0x09, 0x0A]:
            Register = self.i2c.read_i2c_block_data(self.address, 0x14, 6)
            gx = struct.unpack('h',bytes([Register[0],Register[1]]))[0]
            gy = struct.unpack('h',bytes([Register[2],Register[3]]))[0]
            gz = struct.unpack('h',bytes([Register[4],Register[5]]))[0]
            return [gx* 0.001090830782496456,gy* 0.001090830782496456,gz* 0.001090830782496456]
        return (None, None, None)

    @property
    def euler(self):
        """Gives the calculated orientation angles, in degrees.
        Returns an empty tuple of length 3 when this property has been disabled by the current mode.
        """
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            Register = self.i2c.read_i2c_block_data(self.address, 0x1A, 6)
            yaw = struct.unpack('h',bytes([Register[0],Register[1]]))[0]
            roll = struct.unpack('h',bytes([Register[2],Register[3]]))[0]
            pitch = struct.unpack('h',bytes([Register[4],Register[5]]))[0]
            return [-pitch/ 16 ,-roll/ 16 ,((-yaw/ 16) + 180) % 360 - 180]
        return (None, None, None)


    @property
    def quaternion(self):
        """Gives the calculated orientation as a quaternion.
        Returns an empty tuple of length 4 when this property has been disabled by the current mode.
        """
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            Register = self.i2c.read_i2c_block_data(self.address, 0x20, 8)
            qw = struct.unpack('h',bytes([Register[0],Register[1]]))[0]
            qx = struct.unpack('h',bytes([Register[2],Register[3]]))[0]
            qy = struct.unpack('h',bytes([Register[4],Register[5]]))[0]
            qz = struct.unpack('h',bytes([Register[6],Register[7]]))[0]
            return [qw/ (1 << 14),qx/ (1 << 14),qy/ (1 << 14),qz/ (1 << 14)]
        return (None, None, None, None)


    @property
    def linear_acceleration(self):
        """Returns the linear acceleration, without gravity, in m/s.
        Returns an empty tuple of length 3 when this property has been disabled by the current mode.
        """
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            Register = self.i2c.read_i2c_block_data(self.address, 0x28, 6)
            ax = struct.unpack('h',bytes([Register[0],Register[1]]))[0]
            ay = struct.unpack('h',bytes([Register[2],Register[3]]))[0]
            az = struct.unpack('h',bytes([Register[4],Register[5]]))[0]
            return [ax/100,ay/100,az/100]
        return (None, None, None)


    @property
    def gravity(self):
        """Returns the gravity vector, without acceleration in m/s.
        Returns an empty tuple of length 3 when this property has been disabled by the current mode.
        """
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            Register = self.i2c.read_i2c_block_data(self.address, 0x2E, 6)
            gx = struct.unpack('h',bytes([Register[0],Register[1]]))[0]
            gy = struct.unpack('h',bytes([Register[2],Register[3]]))[0]
            gz = struct.unpack('h',bytes([Register[4],Register[5]]))[0]
            return [gx/100,gy/100,gz/100]
        return (None, None, None)

    @property
    def accel_range(self):
        """Switch the accelerometer range and return the new range. Default value: +/- 4g
        See table 3-8 in the datasheet.
        """
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_ACCEL_CONFIG_REGISTER)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        return 0b00000011 & value

    @accel_range.setter
    def accel_range(self, rng: int = ACCEL_4G):
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_ACCEL_CONFIG_REGISTER)
        masked_value = 0b11111100 & value
        self.i2c.write_byte_data(self.address,_ACCEL_CONFIG_REGISTER, masked_value | rng)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)

    @property
    def accel_bandwidth(self):
        """Switch the accelerometer bandwidth and return the new bandwidth. Default value: 62.5 Hz
        See table 3-8 in the datasheet.
        """
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_ACCEL_CONFIG_REGISTER)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        return 0b00011100 & value

    @accel_bandwidth.setter
    def accel_bandwidth(self, bandwidth: int = ACCEL_62_5HZ):
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            raise RuntimeError("Mode must not be a fusion mode")
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_ACCEL_CONFIG_REGISTER)
        masked_value = 0b11100011 & value
        self.i2c.write_byte_data(self.address,_ACCEL_CONFIG_REGISTER, masked_value | bandwidth)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)

    @property
    def accel_mode(self):
        """Switch the accelerometer mode and return the new mode. Default value: Normal
        See table 3-8 in the datasheet.
        """
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_ACCEL_CONFIG_REGISTER)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        return 0b11100000 & value

    @accel_mode.setter
    def accel_mode(self, mode: int = ACCEL_NORMAL_MODE):
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            raise RuntimeError("Mode must not be a fusion mode")
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_ACCEL_CONFIG_REGISTER)
        masked_value = 0b00011111 & value
        self.i2c.write_byte_data(self.address,_ACCEL_CONFIG_REGISTER, masked_value | mode)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)

    @property
    def gyro_range(self):
        """Switch the gyroscope range and return the new range. Default value: 2000 dps
        See table 3-9 in the datasheet.
        """
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_GYRO_CONFIG_0_REGISTER)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        return 0b00000111 & value

    @gyro_range.setter
    def gyro_range(self, rng: int = GYRO_2000_DPS):
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            raise RuntimeError("Mode must not be a fusion mode")
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_GYRO_CONFIG_0_REGISTER)
        masked_value = 0b00111000 & value
        self.i2c.write_byte_data(self.address,_GYRO_CONFIG_0_REGISTER, masked_value | rng)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)

    @property
    def gyro_bandwidth(self):
        """Switch the gyroscope bandwidth and return the new bandwidth. Default value: 32 Hz
        See table 3-9 in the datasheet.
        """
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_GYRO_CONFIG_0_REGISTER)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        return 0b00111000 & value

    @gyro_bandwidth.setter
    def gyro_bandwidth(self, bandwidth: int = GYRO_32HZ):
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            raise RuntimeError("Mode must not be a fusion mode")
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_GYRO_CONFIG_0_REGISTER)
        masked_value = 0b00000111 & value
        self.i2c.write_byte_data(self.address,_GYRO_CONFIG_0_REGISTER, masked_value | bandwidth)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)

    @property
    def gyro_mode(self) -> int:
        """Switch the gyroscope mode and return the new mode. Default value: Normal
        See table 3-9 in the datasheet.
        """
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_GYRO_CONFIG_1_REGISTER)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        return 0b00000111 & value

    @gyro_mode.setter
    def gyro_mode(self, mode: int = GYRO_NORMAL_MODE) -> None:
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            raise RuntimeError("Mode must not be a fusion mode")
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_GYRO_CONFIG_1_REGISTER)
        masked_value = 0b00000000 & value
        self.i2c.write_byte_data(self.address,_GYRO_CONFIG_1_REGISTER, masked_value | mode)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)

    @property
    def magnet_rate(self) -> int:
        """Switch the magnetometer data output rate and return the new rate. Default value: 20Hz
        See table 3-10 in the datasheet.
        """
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_MAGNET_CONFIG_REGISTER)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        return 0b00000111 & value

    @magnet_rate.setter
    def magnet_rate(self, rate: int = MAGNET_20HZ) -> None:
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            raise RuntimeError("Mode must not be a fusion mode")
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_MAGNET_CONFIG_REGISTER)
        masked_value = 0b01111000 & value
        self.i2c.write_byte_data(self.address,_MAGNET_CONFIG_REGISTER, masked_value | rate)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)

    @property
    def magnet_operation_mode(self) -> int:
        """Switch the magnetometer operation mode and return the new mode. Default value: Regular
        See table 3-10 in the datasheet.
        """
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_MAGNET_CONFIG_REGISTER)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        return 0b00011000 & value

    @magnet_operation_mode.setter
    def magnet_operation_mode(self, mode: int = MAGNET_REGULAR_MODE) -> None:
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            raise RuntimeError("Mode must not be a fusion mode")
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_MAGNET_CONFIG_REGISTER)
        masked_value = 0b01100111 & value
        self.i2c.write_byte_data(self.address,_MAGNET_CONFIG_REGISTER, masked_value | mode)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)

    @property
    def magnet_mode(self) -> int:
        """Switch the magnetometer power mode and return the new mode. Default value: Forced
        See table 3-10 in the datasheet.
        """
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_MAGNET_CONFIG_REGISTER)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)
        return 0b01100000 & value

    @magnet_mode.setter
    def magnet_mode(self, mode: int = MAGNET_FORCEMODE_MODE) -> None:
        if self.mode in [0x08, 0x09, 0x0A, 0x0B, 0x0C]:
            raise RuntimeError("Mode must not be a fusion mode")
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x01)
        value = self.i2c.read_byte_data(self.address,_MAGNET_CONFIG_REGISTER)
        masked_value = 0b00011111 & value
        self.i2c.write_byte_data(self.address,_MAGNET_CONFIG_REGISTER, masked_value | mode)
        self.i2c.write_byte_data(self.address,_PAGE_REGISTER, 0x00)

    @property
    def axis_remap(self):
        """Return a tuple with the axis remap register values.

        This will return 6 values with the following meaning:
          - X axis remap (a value of AXIS_REMAP_X, AXIS_REMAP_Y, or AXIS_REMAP_Z.
                          which indicates that the physical X axis of the chip
                          is remapped to a different axis)
          - Y axis remap (see above)
          - Z axis remap (see above)
          - X axis sign (a value of AXIS_REMAP_POSITIVE or AXIS_REMAP_NEGATIVE
                         which indicates if the X axis values should be positive/
                         normal or negative/inverted.  The default is positive.)
          - Y axis sign (see above)
          - Z axis sign (see above)

        Note that the default value, per the datasheet, is NOT P0,
        but rather P1 ()
        """
        # Get the axis remap register value.
        map_config = self.i2c.read_byte_data(self.address,_AXIS_MAP_CONFIG_REGISTER)
        z = (map_config >> 4) & 0x03
        y = (map_config >> 2) & 0x03
        x = map_config & 0x03
        # Get the axis remap sign register value.
        sign_config = self.i2c.read_byte_data(self.address,_AXIS_MAP_SIGN_REGISTER)
        x_sign = (sign_config >> 2) & 0x01
        y_sign = (sign_config >> 1) & 0x01
        z_sign = sign_config & 0x01
        # Return the results as a tuple of all 3 values.
        return (x, y, z, x_sign, y_sign, z_sign)

    @axis_remap.setter
    def axis_remap(self, remap):
        """Pass a tuple consisting of x, y, z, x_sign, y-sign, and z_sign.

        Set axis remap for each axis.  The x, y, z parameter values should
        be set to one of AXIS_REMAP_X (0x00), AXIS_REMAP_Y (0x01), or
        AXIS_REMAP_Z (0x02) and will change the BNO's axis to represent another
        axis.  Note that two axises cannot be mapped to the same axis, so the
        x, y, z params should be a unique combination of AXIS_REMAP_X,
        AXIS_REMAP_Y, AXIS_REMAP_Z values.
        The x_sign, y_sign, z_sign values represent if the axis should be
        positive or negative (inverted). See section 3.4 of the datasheet for
        information on the proper settings for each possible orientation of
        the chip.
        """
        x, y, z, x_sign, y_sign, z_sign = remap
        # Switch to configuration mode. Necessary to remap axes
        current_mode = self.i2c.read_byte_data(self.address,_MODE_REGISTER)
        self.mode = CONFIG_MODE
        # Set the axis remap register value.
        map_config = 0x00
        map_config |= (z & 0x03) << 4
        map_config |= (y & 0x03) << 2
        map_config |= x & 0x03
        self.i2c.write_byte_data(self.address,_AXIS_MAP_CONFIG_REGISTER, map_config)
        # Set the axis remap sign register value.
        sign_config = 0x00
        sign_config |= (x_sign & 0x01) << 2
        sign_config |= (y_sign & 0x01) << 1
        sign_config |= z_sign & 0x01
        self.i2c.write_byte_data(self.address,_AXIS_MAP_SIGN_REGISTER, sign_config)
        # Go back to normal operation mode.
        self.i2c.write_byte_data(self.address,_MODE_REGISTER, current_mode)