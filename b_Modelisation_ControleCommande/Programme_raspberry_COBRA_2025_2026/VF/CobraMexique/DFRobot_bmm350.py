# -*- coding: utf-8 -*
'''
  @file DFRobot_bmm350.py
  @note DFRobot_bmm350 Class infrastructure, implementation of underlying methods
  @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @license     The MIT License (MIT)
  @author      [GDuang](yonglei.ren@dfrobot.com)
  @version     V1.0.0
  @date        2024-05-06
  @url         https://github.com/DFRobot/DFRobot_BMM350
'''
#import serial
import time
import os
import math


# Chip id of BMM350
BMM350_CHIP_ID                              = 0x33

# Variant ID of BMM350
BMM350_MIN_VAR                              = 0x10

# Sensor interface success code
BMM350_INTF_RET_SUCCESS                     = 0

# API success code
BMM350_OK                                   = 0

# API error codes
BMM350_E_NULL_PTR                           = -1
BMM350_E_COM_FAIL                           = -2
BMM350_E_DEV_NOT_FOUND                      = -3
BMM350_E_INVALID_CONFIG                     = -4
BMM350_E_BAD_PAD_DRIVE                      = -5
BMM350_E_RESET_UNFINISHED                   = -6
BMM350_E_INVALID_INPUT                      = -7
BMM350_E_SELF_TEST_INVALID_AXIS             = -8
BMM350_E_OTP_BOOT                           = -9
BMM350_E_OTP_PAGE_RD                        = -10
BMM350_E_OTP_PAGE_PRG                       = -11
BMM350_E_OTP_SIGN                           = -12
BMM350_E_OTP_INV_CMD                        = -13
BMM350_E_OTP_UNDEFINED                      = -14
BMM350_E_ALL_AXIS_DISABLED                  = -15
BMM350_E_PMU_CMD_VALUE                      = -16

BMM350_NO_ERROR                             = 0

# Sensor delay time settings in microseconds
BMM350_SOFT_RESET_DELAY                     = 24000/1000000
BMM350_MAGNETIC_RESET_DELAY                 = 40000/1000000
BMM350_START_UP_TIME_FROM_POR               = 3000/1000000
BMM350_GOTO_SUSPEND_DELAY                   = 6000/1000000
BMM350_SUSPEND_TO_NORMAL_DELAY              = 38000/1000000
BMM350_SUS_TO_FORCEDMODE_NO_AVG_DELAY       = 15000/1000000
BMM350_SUS_TO_FORCEDMODE_AVG_2_DELAY        = 17000/1000000
BMM350_SUS_TO_FORCEDMODE_AVG_4_DELAY        = 20000/1000000
BMM350_SUS_TO_FORCEDMODE_AVG_8_DELAY        = 28000/1000000
BMM350_SUS_TO_FORCEDMODE_FAST_NO_AVG_DELAY  = 4000/1000000
BMM350_SUS_TO_FORCEDMODE_FAST_AVG_2_DELAY   = 5000/1000000
BMM350_SUS_TO_FORCEDMODE_FAST_AVG_4_DELAY   = 9000/1000000
BMM350_SUS_TO_FORCEDMODE_FAST_AVG_8_DELAY   = 16000/1000000
BMM350_UPD_OAE_DELAY                        = 1000/1000000
BMM350_BR_DELAY                             = 14000/1000000
BMM350_FGR_DELAY                            = 18000/1000000

# Length macros
BMM350_OTP_DATA_LENGTH                      = 32
BMM350_READ_BUFFER_LENGTH                   = 127
BMM350_MAG_TEMP_DATA_LEN                    = 12

# Averaging macros
BMM350_AVG_NO_AVG                           = 0x0
BMM350_AVG_2                                = 0x1
BMM350_AVG_4                                = 0x2
BMM350_AVG_8                                = 0x3

# ODR
BMM350_ODR_400HZ                            = 0x2
BMM350_ODR_200HZ                            = 0x3
BMM350_ODR_100HZ                            = 0x4
BMM350_ODR_50HZ                             = 0x5
BMM350_ODR_25HZ                             = 0x6
BMM350_ODR_12_5HZ                           = 0x7   # default rate
BMM350_ODR_6_25HZ                           = 0x8
BMM350_ODR_3_125HZ                          = 0x9
BMM350_ODR_1_5625HZ                         = 0xA

# Power modes
BMM350_PMU_CMD_SUS                          = 0x00
BMM350_PMU_CMD_NM                           = 0x01
BMM350_PMU_CMD_UPD_OAE                      = 0x02
BMM350_PMU_CMD_FM                           = 0x03
BMM350_PMU_CMD_FM_FAST                      = 0x04
BMM350_PMU_CMD_FGR                          = 0x05
BMM350_PMU_CMD_FGR_FAST                     = 0x06
BMM350_PMU_CMD_BR                           = 0x07
BMM350_PMU_CMD_BR_FAST                      = 0x08
BMM350_PMU_CMD_NM_TC                        = 0x09

BMM350_PMU_STATUS_0                         = 0x0

BMM350_DISABLE                              = 0x0
BMM350_ENABLE                               = 0x1
BMM350_MAP_TO_PIN                           = BMM350_ENABLE

BMM350_CMD_NOP                              = 0x0
BMM350_CMD_SOFTRESET                        = 0xB6

BMM350_TARGET_PAGE_PAGE0                    = 0x0
BMM350_TARGET_PAGE_PAGE1                    = 0x1

BMM350_INT_MODE_LATCHED                     = 0x1
BMM350_INT_MODE_PULSED                      = 0x0

BMM350_INT_POL_ACTIVE_HIGH                  = 0x1
BMM350_INT_POL_ACTIVE_LOW                   = 0x0

BMM350_INT_OD_PUSHPULL                      = 0x1
BMM350_INT_OD_OPENDRAIN                     = 0x0

BMM350_INT_OUTPUT_EN_OFF                    = 0x0
BMM350_INT_OUTPUT_EN_ON                     = 0x1

BMM350_INT_DRDY_EN                          = 0x1
BMM350_INT_DRDY_DIS                         = 0x0

BMM350_MR_MR1K8                             = 0x0
BMM350_MR_MR2K1                             = 0x1
BMM350_MR_MR1K5                             = 0x2
BMM350_MR_MR0K6                             = 0x3

BMM350_SEL_DTB1X_PAD_PAD_INT                = 0x0
BMM350_SEL_DTB1X_PAD_PAD_BYP                = 0x1

BMM350_TMR_TST_HIZ_VTMR_VTMR_ON             = 0x0
BMM350_TMR_TST_HIZ_VTMR_VTMR_HIZ            = 0x1

BMM350_LSB_MASK                             = 0x00FF
BMM350_MSB_MASK                             = 0xFF00

# Pad drive strength
BMM350_PAD_DRIVE_WEAKEST                    = 0
BMM350_PAD_DRIVE_STRONGEST                  = 7

# I2C Register Addresses

# Register to set I2C address to LOW
BMM350_I2C_ADSEL_SET_LOW                    = 0x14

# Register to set I2C address to HIGH
BMM350_I2C_ADSEL_SET_HIGH                   = 0x15

BMM350_DUMMY_BYTES                          = 2

# Register Addresses

BMM350_REG_CHIP_ID                          = 0x00
BMM350_REG_REV_ID                           = 0x01
BMM350_REG_ERR_REG                          = 0x02
BMM350_REG_PAD_CTRL                         = 0x03
BMM350_REG_PMU_CMD_AGGR_SET                 = 0x04
BMM350_REG_PMU_CMD_AXIS_EN                  = 0x05
BMM350_REG_PMU_CMD                          = 0x06
BMM350_REG_PMU_CMD_STATUS_0                 = 0x07
BMM350_REG_PMU_CMD_STATUS_1                 = 0x08
BMM350_REG_I3C_ERR                          = 0x09
BMM350_REG_I2C_WDT_SET                      = 0x0A
BMM350_REG_TRSDCR_REV_ID                    = 0x0D
BMM350_REG_TC_SYNC_TU                       = 0x21
BMM350_REG_TC_SYNC_ODR                      = 0x22
BMM350_REG_TC_SYNC_TPH_1                    = 0x23
BMM350_REG_TC_SYNC_TPH_2                    = 0x24
BMM350_REG_TC_SYNC_DT                       = 0x25
BMM350_REG_TC_SYNC_ST_0                     = 0x26
BMM350_REG_TC_SYNC_ST_1                     = 0x27
BMM350_REG_TC_SYNC_ST_2                     = 0x28
BMM350_REG_TC_SYNC_STATUS                   = 0x29
BMM350_REG_INT_CTRL                         = 0x2E
BMM350_REG_INT_CTRL_IBI                     = 0x2F
BMM350_REG_INT_STATUS                       = 0x30
BMM350_REG_MAG_X_XLSB                       = 0x31
BMM350_REG_MAG_X_LSB                        = 0x32
BMM350_REG_MAG_X_MSB                        = 0x33
BMM350_REG_MAG_Y_XLSB                       = 0x34
BMM350_REG_MAG_Y_LSB                        = 0x35
BMM350_REG_MAG_Y_MSB                        = 0x36
BMM350_REG_MAG_Z_XLSB                       = 0x37
BMM350_REG_MAG_Z_LSB                        = 0x38
BMM350_REG_MAG_Z_MSB                        = 0x39
BMM350_REG_TEMP_XLSB                        = 0x3A
BMM350_REG_TEMP_LSB                         = 0x3B
BMM350_REG_TEMP_MSB                         = 0x3C
BMM350_REG_SENSORTIME_XLSB                  = 0x3D
BMM350_REG_SENSORTIME_LSB                   = 0x3E
BMM350_REG_SENSORTIME_MSB                   = 0x3F
BMM350_REG_OTP_CMD_REG                      = 0x50
BMM350_REG_OTP_DATA_MSB_REG                 = 0x52
BMM350_REG_OTP_DATA_LSB_REG                 = 0x53
BMM350_REG_OTP_STATUS_REG                   = 0x55
BMM350_REG_TMR_SELFTEST_USER                = 0x60
BMM350_REG_CTRL_USER                        = 0x61
BMM350_REG_CMD                              = 0x7E

# Macros for OVWR
BMM350_REG_OVWR_VALUE_ANA_0                 = 0x3A
BMM350_REG_OVWR_EN_ANA_0                    = 0x3B

# Macros for bit masking

BMM350_CHIP_ID_OTP_MSK                      = 0xf
BMM350_CHIP_ID_OTP_POS                      = 0x0
BMM350_CHIP_ID_FIXED_MSK                    = 0xf0
BMM350_CHIP_ID_FIXED_POS                    = 0x4
BMM350_REV_ID_MAJOR_MSK                     = 0xf0
BMM350_REV_ID_MAJOR_POS                     = 0x4
BMM350_REV_ID_MINOR_MSK                     = 0xf
BMM350_REV_ID_MINOR_POS                     = 0x0
BMM350_PMU_CMD_ERROR_MSK                    = 0x1
BMM350_PMU_CMD_ERROR_POS                    = 0x0
BMM350_BOOT_UP_ERROR_MSK                    = 0x2
BMM350_BOOT_UP_ERROR_POS                    = 0x1
BMM350_DRV_MSK                              = 0x7
BMM350_DRV_POS                              = 0x0
BMM350_AVG_MSK                              = 0x30
BMM350_AVG_POS                              = 0x4
BMM350_ODR_MSK                              = 0xf
BMM350_ODR_POS                              = 0x0
BMM350_PMU_CMD_MSK                          = 0xf
BMM350_PMU_CMD_POS                          = 0x0
BMM350_EN_X_MSK                             = 0x01
BMM350_EN_X_POS                             = 0x0
BMM350_EN_Y_MSK                             = 0x02
BMM350_EN_Y_POS                             = 0x1
BMM350_EN_Z_MSK                             = 0x04
BMM350_EN_Z_POS                             = 0x2
BMM350_EN_XYZ_MSK                           = 0x7
BMM350_EN_XYZ_POS                           = 0x0
BMM350_PMU_CMD_BUSY_MSK                     = 0x1
BMM350_PMU_CMD_BUSY_POS                     = 0x0
BMM350_ODR_OVWR_MSK                         = 0x2
BMM350_ODR_OVWR_POS                         = 0x1
BMM350_AVG_OVWR_MSK                         = 0x4
BMM350_AVG_OVWR_POS                         = 0x2
BMM350_PWR_MODE_IS_NORMAL_MSK               = 0x8
BMM350_PWR_MODE_IS_NORMAL_POS               = 0x3
BMM350_CMD_IS_ILLEGAL_MSK                   = 0x10
BMM350_CMD_IS_ILLEGAL_POS                   = 0x4
BMM350_PMU_CMD_VALUE_MSK                    = 0xE0
BMM350_PMU_CMD_VALUE_POS                    = 0x5
BMM350_PMU_ODR_S_MSK                        = 0xf
BMM350_PMU_ODR_S_POS                        = 0x0
BMM350_PMU_AVG_S_MSK                        = 0x30
BMM350_PMU_AVG_S_POS                        = 0x4
BMM350_I3C_ERROR_0_MSK                      = 0x1
BMM350_I3C_ERROR_0_POS                      = 0x0
BMM350_I3C_ERROR_3_MSK                      = 0x8
BMM350_I3C_ERROR_3_POS                      = 0x3
BMM350_I2C_WDT_EN_MSK                       = 0x1
BMM350_I2C_WDT_EN_POS                       = 0x0
BMM350_I2C_WDT_SEL_MSK                      = 0x2

BMM350_I2C_WDT_SEL_POS                      = 0x1
BMM350_TRSDCR_REV_ID_OTP_MSK                = 0x3
BMM350_TRSDCR_REV_ID_OTP_POS                = 0x0
BMM350_TRSDCR_REV_ID_FIXED_MSK              = 0xfc
BMM350_TRSDCR_REV_ID_FIXED_POS              = 0x2
BMM350_PAGING_EN_MSK                        = 0x80
BMM350_PAGING_EN_POS                        = 0x7
BMM350_DRDY_DATA_REG_MSK                    = 0x4
BMM350_DRDY_DATA_REG_POS                    = 0x2
BMM350_INT_MODE_MSK                         = 0x1
BMM350_INT_MODE_POS                         = 0x0
BMM350_INT_POL_MSK                          = 0x2
BMM350_INT_POL_POS                          = 0x1
BMM350_INT_OD_MSK                           = 0x4
BMM350_INT_OD_POS                           = 0x2
BMM350_INT_OUTPUT_EN_MSK                    = 0x8
BMM350_INT_OUTPUT_EN_POS                    = 0x3
BMM350_DRDY_DATA_REG_EN_MSK                 = 0x80
BMM350_DRDY_DATA_REG_EN_POS                 = 0x7
BMM350_DRDY_INT_MAP_TO_IBI_MSK              = 0x1
BMM350_DRDY_INT_MAP_TO_IBI_POS              = 0x0
BMM350_CLEAR_DRDY_INT_STATUS_UPON_IBI_MSK   = 0x10
BMM350_CLEAR_DRDY_INT_STATUS_UPON_IBI_POS   = 0x4
BMM350_TC_SYNC_TU_MSK                       = 0xff
BMM350_TC_SYNC_ODR_MSK                      = 0xff
BMM350_TC_SYNC_TPH_1_MSK                    = 0xff
BMM350_TC_SYNC_TPH_2_MSK                    = 0xff
BMM350_TC_SYNC_DT_MSK                       = 0xff
BMM350_TC_SYNC_ST_0_MSK                     = 0xff
BMM350_TC_SYNC_ST_1_MSK                     = 0xff
BMM350_TC_SYNC_ST_2_MSK                     = 0xff
BMM350_CFG_FORCE_SOSC_EN_MSK                = 0x4
BMM350_CFG_FORCE_SOSC_EN_POS                = 0x2
BMM350_ST_IGEN_EN_MSK                       = 0x1
BMM350_ST_IGEN_EN_POS                       = 0x0
BMM350_ST_N_MSK                             = 0x2
BMM350_ST_N_POS                             = 0x1
BMM350_ST_P_MSK                             = 0x4
BMM350_ST_P_POS                             = 0x2
BMM350_IST_EN_X_MSK                         = 0x8
BMM350_IST_EN_X_POS                         = 0x3
BMM350_IST_EN_Y_MSK                         = 0x10
BMM350_IST_EN_Y_POS                         = 0x4
BMM350_CFG_SENS_TIM_AON_MSK                 = 0x1
BMM350_CFG_SENS_TIM_AON_POS                 = 0x0
BMM350_DATA_X_7_0_MSK                       = 0xff
BMM350_DATA_X_7_0_POS                       = 0x0
BMM350_DATA_X_15_8_MSK                      = 0xff
BMM350_DATA_X_15_8_POS                      = 0x0
BMM350_DATA_X_23_16_MSK                     = 0xff
BMM350_DATA_X_23_16_POS                     = 0x0
BMM350_DATA_Y_7_0_MSK                       = 0xff
BMM350_DATA_Y_7_0_POS                       = 0x0
BMM350_DATA_Y_15_8_MSK                      = 0xff
BMM350_DATA_Y_15_8_POS                      = 0x0
BMM350_DATA_Y_23_16_MSK                     = 0xff
BMM350_DATA_Y_23_16_POS                     = 0x0
BMM350_DATA_Z_7_0_MSK                       = 0xff
BMM350_DATA_Z_7_0_POS                       = 0x0
BMM350_DATA_Z_15_8_MSK                      = 0xff
BMM350_DATA_Z_15_8_POS                      = 0x0
BMM350_DATA_Z_23_16_MSK                     = 0xff
BMM350_DATA_Z_23_16_POS                     = 0x0
BMM350_DATA_T_7_0_MSK                       = 0xff
BMM350_DATA_T_7_0_POS                       = 0x0
BMM350_DATA_T_15_8_MSK                      = 0xff
BMM350_DATA_T_15_8_POS                      = 0x0
BMM350_DATA_T_23_16_MSK                     = 0xff
BMM350_DATA_T_23_16_POS                     = 0x0
BMM350_DATA_ST_7_0_MSK                      = 0xff
BMM350_DATA_ST_7_0_POS                      = 0x0
BMM350_DATA_ST_15_8_MSK                     = 0xff
BMM350_DATA_ST_15_8_POS                     = 0x0
BMM350_DATA_ST_23_16_MSK                    = 0xff
BMM350_DATA_ST_23_16_POS                    = 0x0
BMM350_SIGN_INVERT_T_MSK                    = 0x10
BMM350_SIGN_INVERT_T_POS                    = 0x4
BMM350_SIGN_INVERT_X_MSK                    = 0x20
BMM350_SIGN_INVERT_X_POS                    = 0x5
BMM350_SIGN_INVERT_Y_MSK                    = 0x40
BMM350_SIGN_INVERT_Y_POS                    = 0x6
BMM350_SIGN_INVERT_Z_MSK                    = 0x80
BMM350_SIGN_INVERT_Z_POS                    = 0x7
BMM350_DIS_BR_NM_MSK                        = 0x1
BMM350_DIS_BR_NM_POS                        = 0x0
BMM350_DIS_FGR_NM_MSK                       = 0x2
BMM350_DIS_FGR_NM_POS                       = 0x1
BMM350_DIS_CRST_AT_ALL_MSK                  = 0x4
BMM350_DIS_CRST_AT_ALL_POS                  = 0x2
BMM350_DIS_BR_FM_MSK                        = 0x8
BMM350_DIS_BR_FM_POS                        = 0x3
BMM350_FRC_EN_BUFF_MSK                      = 0x1
BMM350_FRC_EN_BUFF_POS                      = 0x0
BMM350_FRC_INA_EN1_MSK                      = 0x2
BMM350_FRC_INA_EN1_POS                      = 0x1
BMM350_FRC_INA_EN2_MSK                      = 0x4
BMM350_FRC_INA_EN2_POS                      = 0x2
BMM350_FRC_ADC_EN_MSK                       = 0x8
BMM350_FRC_ADC_EN_POS                       = 0x3
BMM350_FRC_INA_RST_MSK                      = 0x10
BMM350_FRC_INA_RST_POS                      = 0x4
BMM350_FRC_ADC_RST_MSK                      = 0x20
BMM350_FRC_ADC_RST_POS                      = 0x5
BMM350_FRC_INA_XSEL_MSK                     = 0x1
BMM350_FRC_INA_XSEL_POS                     = 0x0
BMM350_FRC_INA_YSEL_MSK                     = 0x2
BMM350_FRC_INA_YSEL_POS                     = 0x1
BMM350_FRC_INA_ZSEL_MSK                     = 0x4
BMM350_FRC_INA_ZSEL_POS                     = 0x2
BMM350_FRC_ADC_TEMP_EN_MSK                  = 0x8
BMM350_FRC_ADC_TEMP_EN_POS                  = 0x3
BMM350_FRC_TSENS_EN_MSK                     = 0x10
BMM350_FRC_TSENS_EN_POS                     = 0x4
BMM350_DSENS_FM_MSK                         = 0x20
BMM350_DSENS_FM_POS                         = 0x5
BMM350_DSENS_SEL_MSK                        = 0x40
BMM350_DSENS_SEL_POS                        = 0x6
BMM350_DSENS_SHORT_MSK                      = 0x80
BMM350_DSENS_SHORT_POS                      = 0x7
BMM350_ERR_MISS_BR_DONE_MSK                 = 0x1
BMM350_ERR_MISS_BR_DONE_POS                 = 0x0
BMM350_ERR_MISS_FGR_DONE_MSK                = 0x2
BMM350_ERR_MISS_FGR_DONE_POS                = 0x1
BMM350_TST_CHAIN_LN_MODE_MSK                = 0x1
BMM350_TST_CHAIN_LN_MODE_POS                = 0x0
BMM350_TST_CHAIN_LP_MODE_MSK                = 0x2
BMM350_TST_CHAIN_LP_MODE_POS                = 0x1
BMM350_EN_OVWR_TMR_IF_MSK                   = 0x1
BMM350_EN_OVWR_TMR_IF_POS                   = 0x0
BMM350_TMR_CKTRIGB_MSK                      = 0x2
BMM350_TMR_CKTRIGB_POS                      = 0x1
BMM350_TMR_DO_BR_MSK                        = 0x4
BMM350_TMR_DO_BR_POS                        = 0x2
BMM350_TMR_DO_FGR_MSK                       = 0x18
BMM350_TMR_DO_FGR_POS                       = 0x3
BMM350_TMR_EN_OSC_MSK                       = 0x80
BMM350_TMR_EN_OSC_POS                       = 0x7
BMM350_VCM_TRIM_X_MSK                       = 0x1f
BMM350_VCM_TRIM_X_POS                       = 0x0
BMM350_VCM_TRIM_Y_MSK                       = 0x1f
BMM350_VCM_TRIM_Y_POS                       = 0x0
BMM350_VCM_TRIM_Z_MSK                       = 0x1f
BMM350_VCM_TRIM_Z_POS                       = 0x0
BMM350_VCM_TRIM_DSENS_MSK                   = 0x1f
BMM350_VCM_TRIM_DSENS_POS                   = 0x0
BMM350_TWLB_MSK                             = 0x30
BMM350_TWLB_POS                             = 0x4
BMM350_PRG_PLS_TIM_MSK                      = 0x30
BMM350_PRG_PLS_TIM_POS                      = 0x4
BMM350_OTP_OVWR_EN_MSK                      = 0x1
BMM350_OTP_OVWR_EN_POS                      = 0x0
BMM350_OTP_MEM_CLK_MSK                      = 0x2
BMM350_OTP_MEM_CLK_POS                      = 0x1
BMM350_OTP_MEM_CS_MSK                       = 0x4
BMM350_OTP_MEM_CS_POS                       = 0x2
BMM350_OTP_MEM_PGM_MSK                      = 0x8
BMM350_OTP_MEM_PGM_POS                      = 0x3
BMM350_OTP_MEM_RE_MSK                       = 0x10
BMM350_OTP_MEM_RE_POS                       = 0x4
BMM350_SAMPLE_RDATA_PLS_MSK                 = 0x80
BMM350_SAMPLE_RDATA_PLS_POS                 = 0x7
BMM350_CFG_FW_MSK                           = 0x1
BMM350_CFG_FW_POS                           = 0x0
BMM350_EN_BR_X_MSK                          = 0x2
BMM350_EN_BR_X_POS                          = 0x1
BMM350_EN_BR_Y_MSK                          = 0x4
BMM350_EN_BR_Y_POS                          = 0x2
BMM350_EN_BR_Z_MSK                          = 0x8
BMM350_EN_BR_Z_POS                          = 0x3
BMM350_CFG_PAUSE_TIME_MSK                   = 0x30
BMM350_CFG_PAUSE_TIME_POS                   = 0x4
BMM350_CFG_FGR_PLS_DUR_MSK                  = 0xf
BMM350_CFG_FGR_PLS_DUR_POS                  = 0x0
BMM350_CFG_BR_Z_ORDER_MSK                   = 0x10
BMM350_CFG_BR_Z_ORDER_POS                   = 0x4
BMM350_CFG_BR_XY_CHOP_MSK                   = 0x20
BMM350_CFG_BR_XY_CHOP_POS                   = 0x5
BMM350_CFG_BR_PLS_DUR_MSK                   = 0xc0
BMM350_CFG_BR_PLS_DUR_POS                   = 0x6
BMM350_ENABLE_BR_FGR_TEST_MSK               = 0x1
BMM350_ENABLE_BR_FGR_TEST_POS               = 0x0
BMM350_SEL_AXIS_MSK                         = 0xe
BMM350_SEL_AXIS_POS                         = 0x1
BMM350_TMR_CFG_TEST_CLK_EN_MSK              = 0x10
BMM350_TMR_CFG_TEST_CLK_EN_POS              = 0x4
BMM350_TEST_VAL_BITS_7DOWNTO0_MSK           = 0xff
BMM350_TEST_VAL_BITS_7DOWNTO0_POS           = 0x0
BMM350_TEST_VAL_BITS_8_MSK                  = 0x1
BMM350_TEST_VAL_BITS_8_POS                  = 0x0
BMM350_TEST_P_SAMPLE_MSK                    = 0x2
BMM350_TEST_P_SAMPLE_POS                    = 0x1
BMM350_TEST_N_SAMPLE_MSK                    = 0x4
BMM350_TEST_N_SAMPLE_POS                    = 0x2
BMM350_TEST_APPLY_TO_REM_MSK                = 0x10
BMM350_TEST_APPLY_TO_REM_POS                = 0x4
BMM350_UFO_TRM_OSC_RANGE_MSK                = 0xf
BMM350_UFO_TRM_OSC_RANGE_POS                = 0x0
BMM350_ISO_CHIP_ID_MSK                      = 0x78
BMM350_ISO_CHIP_ID_POS                      = 0x3
BMM350_ISO_I2C_DEV_ID_MSK                   = 0x80
BMM350_ISO_I2C_DEV_ID_POS                   = 0x7
BMM350_I3C_FREQ_BITS_1DOWNTO0_MSK           = 0xc
BMM350_I3C_FREQ_BITS_1DOWNTO0_POS           = 0x2
BMM350_I3C_IBI_MDB_SEL_MSK                  = 0x10
BMM350_I3C_IBI_MDB_SEL_POS                  = 0x4
BMM350_TC_ASYNC_EN_MSK                      = 0x20
BMM350_TC_ASYNC_EN_POS                      = 0x5
BMM350_TC_SYNC_EN_MSK                       = 0x40
BMM350_TC_SYNC_EN_POS                       = 0x6
BMM350_I3C_SCL_GATING_EN_MSK                = 0x80
BMM350_I3C_SCL_GATING_EN_POS                = 0x7
BMM350_I3C_INACCURACY_BITS_6DOWNTO0_MSK     = 0x7f
BMM350_I3C_INACCURACY_BITS_6DOWNTO0_POS     = 0x0
BMM350_EST_EN_X_MSK                         = 0x1
BMM350_EST_EN_X_POS                         = 0x0
BMM350_EST_EN_Y_MSK                         = 0x2
BMM350_EST_EN_Y_POS                         = 0x1
BMM350_CRST_DIS_MSK                         = 0x4
BMM350_CRST_DIS_POS                         = 0x2
BMM350_BR_TFALL_MSK                         = 0x7
BMM350_BR_TFALL_POS                         = 0x0
BMM350_BR_TRISE_MSK                         = 0x70
BMM350_BR_TRISE_POS                         = 0x4
BMM350_TMR_SOFT_START_DIS_MSK               = 0x80
BMM350_TMR_SOFT_START_DIS_POS               = 0x7
BMM350_FOSC_LOW_RANGE_MSK                   = 0x80
BMM350_FOSC_LOW_RANGE_POS                   = 0x7
BMM350_VCRST_TRIM_FG_MSK                    = 0x3f
BMM350_VCRST_TRIM_FG_POS                    = 0x0
BMM350_VCRST_TRIM_BR_MSK                    = 0x3f
BMM350_VCRST_TRIM_BR_POS                    = 0x0
BMM350_BG_TRIM_VRP_MSK                      = 0xc0
BMM350_BG_TRIM_VRP_POS                      = 0x6
BMM350_BG_TRIM_TC_MSK                       = 0xf
BMM350_BG_TRIM_TC_POS                       = 0x0
BMM350_BG_TRIM_VRA_MSK                      = 0xf0
BMM350_BG_TRIM_VRA_POS                      = 0x4
BMM350_BG_TRIM_VRD_MSK                      = 0xf
BMM350_BG_TRIM_VRD_POS                      = 0x0
BMM350_OVWR_REF_IB_EN_MSK                   = 0x10
BMM350_OVWR_REF_IB_EN_POS                   = 0x4
BMM350_OVWR_VDDA_EN_MSK                     = 0x20
BMM350_OVWR_VDDA_EN_POS                     = 0x5
BMM350_OVWR_VDDP_EN_MSK                     = 0x40
BMM350_OVWR_VDDP_EN_POS                     = 0x6
BMM350_OVWR_VDDS_EN_MSK                     = 0x80
BMM350_OVWR_VDDS_EN_POS                     = 0x7
BMM350_REF_IB_EN_MSK                        = 0x10
BMM350_REF_IB_EN_POS                        = 0x4
BMM350_VDDA_EN_MSK                          = 0x20
BMM350_VDDA_EN_POS                          = 0x5
BMM350_VDDP_EN_MSK                          = 0x40
BMM350_VDDP_EN_POS                          = 0x6
BMM350_VDDS_EN_MSK                          = 0x80
BMM350_VDDS_EN_POS                          = 0x7
BMM350_OVWR_OTP_PROG_VDD_SW_EN_MSK          = 0x8
BMM350_OVWR_OTP_PROG_VDD_SW_EN_POS          = 0x3
BMM350_OVWR_EN_MFE_BG_FILT_BYPASS_MSK       = 0x10
BMM350_OVWR_EN_MFE_BG_FILT_BYPASS_POS       = 0x4
BMM350_OTP_PROG_VDD_SW_EN_MSK               = 0x8
BMM350_OTP_PROG_VDD_SW_EN_POS               = 0x3
BMM350_CP_COMP_CRST_EN_TM_MSK               = 0x10
BMM350_CP_COMP_CRST_EN_TM_POS               = 0x4
BMM350_CP_COMP_VDD_EN_TM_MSK                = 0x20
BMM350_CP_COMP_VDD_EN_TM_POS                = 0x5
BMM350_CP_INTREFS_EN_TM_MSK                 = 0x40
BMM350_CP_INTREFS_EN_TM_POS                 = 0x6
BMM350_ADC_LOCAL_CHOP_EN_MSK                = 0x20
BMM350_ADC_LOCAL_CHOP_EN_POS                = 0x5
BMM350_INA_MODE_MSK                         = 0x40
BMM350_INA_MODE_POS                         = 0x6
BMM350_VDDD_EXT_EN_MSK                      = 0x20
BMM350_VDDD_EXT_EN_POS                      = 0x5
BMM350_VDDP_EXT_EN_MSK                      = 0x80
BMM350_VDDP_EXT_EN_POS                      = 0x7
BMM350_ADC_DSENS_EN_MSK                     = 0x10
BMM350_ADC_DSENS_EN_POS                     = 0x4
BMM350_DSENS_EN_MSK                         = 0x20
BMM350_DSENS_EN_POS                         = 0x5
BMM350_OTP_TM_CLVWR_EN_MSK                  = 0x40
BMM350_OTP_TM_CLVWR_EN_POS                  = 0x6
BMM350_OTP_VDDP_DIS_MSK                     = 0x80
BMM350_OTP_VDDP_DIS_POS                     = 0x7
BMM350_FORCE_HIGH_VREF_IREF_OK_MSK          = 0x10
BMM350_FORCE_HIGH_VREF_IREF_OK_POS          = 0x4
BMM350_FORCE_HIGH_FOSC_OK_MSK               = 0x20
BMM350_FORCE_HIGH_FOSC_OK_POS               = 0x5
BMM350_FORCE_HIGH_MFE_BG_RDY_MSK            = 0x40
BMM350_FORCE_HIGH_MFE_BG_RDY_POS            = 0x6
BMM350_FORCE_HIGH_MFE_VTMR_RDY_MSK          = 0x80
BMM350_FORCE_HIGH_MFE_VTMR_RDY_POS          = 0x7
BMM350_ERR_END_OF_RECHARGE_MSK              = 0x1
BMM350_ERR_END_OF_RECHARGE_POS              = 0x0
BMM350_ERR_END_OF_DISCHARGE_MSK             = 0x2
BMM350_ERR_END_OF_DISCHARGE_POS             = 0x1
BMM350_CP_TMX_DIGTP_SEL_MSK                 = 0x7
BMM350_CP_TMX_DIGTP_SEL_POS                 = 0x0
BMM350_CP_CPOSC_EN_TM_MSK                   = 0x80
BMM350_CP_CPOSC_EN_TM_POS                   = 0x7
BMM350_TST_ATM1_CFG_MSK                     = 0x3f
BMM350_TST_ATM1_CFG_POS                     = 0x0
BMM350_TST_TB1_EN_MSK                       = 0x80
BMM350_TST_TB1_EN_POS                       = 0x7
BMM350_TST_ATM2_CFG_MSK                     = 0x1f
BMM350_TST_ATM2_CFG_POS                     = 0x0
BMM350_TST_TB2_EN_MSK                       = 0x80
BMM350_TST_TB2_EN_POS                       = 0x7
BMM350_REG_DTB1X_SEL_MSK                    = 0x7f
BMM350_REG_DTB1X_SEL_POS                    = 0x0
BMM350_SEL_DTB1X_PAD_MSK                    = 0x80
BMM350_SEL_DTB1X_PAD_POS                    = 0x7
BMM350_REG_DTB2X_SEL_MSK                    = 0x7f
BMM350_REG_DTB2X_SEL_POS                    = 0x0
BMM350_TMR_TST_CFG_MSK                      = 0x7f
BMM350_TMR_TST_CFG_POS                      = 0x0
BMM350_TMR_TST_HIZ_VTMR_MSK                 = 0x80
BMM350_TMR_TST_HIZ_VTMR_POS                 = 0x7

# OTP MACROS
BMM350_OTP_CMD_DIR_READ                     = 0x20
BMM350_OTP_CMD_DIR_PRGM_1B                  = 0x40
BMM350_OTP_CMD_DIR_PRGM                     = 0x60
BMM350_OTP_CMD_PWR_OFF_OTP                  = 0x80
BMM350_OTP_CMD_EXT_READ                     = 0xA0
BMM350_OTP_CMD_EXT_PRGM                     = 0xE0
BMM350_OTP_CMD_MSK                          = 0xE0
BMM350_OTP_WORD_ADDR_MSK                    = 0x1F

BMM350_OTP_STATUS_ERROR_MSK                 = 0xE0
BMM350_OTP_STATUS_NO_ERROR                  = 0x00
BMM350_OTP_STATUS_BOOT_ERR                  = 0x20
BMM350_OTP_STATUS_PAGE_RD_ERR               = 0x40
BMM350_OTP_STATUS_PAGE_PRG_ERR              = 0x60
BMM350_OTP_STATUS_SIGN_ERR                  = 0x80
BMM350_OTP_STATUS_INV_CMD_ERR               = 0xA0
BMM350_OTP_STATUS_CMD_DONE                  = 0x01

# OTP indices
BMM350_TEMP_OFF_SENS                        = 0x0D

BMM350_MAG_OFFSET_X                         = 0x0E
BMM350_MAG_OFFSET_Y                         = 0x0F
BMM350_MAG_OFFSET_Z                         = 0x10

BMM350_MAG_SENS_X                           = 0x10
BMM350_MAG_SENS_Y                           = 0x11
BMM350_MAG_SENS_Z                           = 0x11

BMM350_MAG_TCO_X                            = 0x12
BMM350_MAG_TCO_Y                            = 0x13
BMM350_MAG_TCO_Z                            = 0x14

BMM350_MAG_TCS_X                            = 0x12
BMM350_MAG_TCS_Y                            = 0x13
BMM350_MAG_TCS_Z                            = 0x14

BMM350_MAG_DUT_T_0                          = 0x18

BMM350_CROSS_X_Y                            = 0x15
BMM350_CROSS_Y_X                            = 0x15
BMM350_CROSS_Z_X                            = 0x16
BMM350_CROSS_Z_Y                            = 0x16

BMM350_SENS_CORR_Y                          = 0.01
BMM350_TCS_CORR_Z                           = 0.000

# Signed bit macros
BMM350_SIGNED_8_BIT                         = 8
BMM350_SIGNED_12_BIT                        = 12
BMM350_SIGNED_16_BIT                        = 16
BMM350_SIGNED_21_BIT                        = 21
BMM350_SIGNED_24_BIT                        = 24

# Self-test macros
BMM350_SELF_TEST_DISABLE                    = 0x00
BMM350_SELF_TEST_POS_X                      = 0x0D
BMM350_SELF_TEST_NEG_X                      = 0x0B
BMM350_SELF_TEST_POS_Y                      = 0x15
BMM350_SELF_TEST_NEG_Y                      = 0x13

BMM350_X_FM_XP_UST_MAX_LIMIT                = 150
BMM350_X_FM_XP_UST_MIN_LIMIT                = 50

BMM350_X_FM_XN_UST_MAX_LIMIT                = -50
BMM350_X_FM_XN_UST_MIN_LIMIT                = -150

BMM350_Y_FM_YP_UST_MAX_LIMIT                = 150
BMM350_Y_FM_YP_UST_MIN_LIMIT                = 50

BMM350_Y_FM_YN_UST_MAX_LIMIT                = -50
BMM350_Y_FM_YN_UST_MIN_LIMIT                = -150

# PMU command status 0 macros
BMM350_PMU_CMD_STATUS_0_SUS                 = 0x00
BMM350_PMU_CMD_STATUS_0_NM                  = 0x01
BMM350_PMU_CMD_STATUS_0_UPD_OAE             = 0x02
BMM350_PMU_CMD_STATUS_0_FM                  = 0x03
BMM350_PMU_CMD_STATUS_0_FM_FAST             = 0x04
BMM350_PMU_CMD_STATUS_0_FGR                 = 0x05
BMM350_PMU_CMD_STATUS_0_FGR_FAST            = 0x06
BMM350_PMU_CMD_STATUS_0_BR                  = 0x07
BMM350_PMU_CMD_STATUS_0_BR_FAST             = 0x07


# PRESET MODE DEFINITIONS
BMM350_PRESETMODE_LOWPOWER                = 0x01
BMM350_PRESETMODE_REGULAR                 = 0x02
BMM350_PRESETMODE_HIGHACCURACY            = 0x03
BMM350_PRESETMODE_ENHANCED                = 0x04

LOW_THRESHOLD_INTERRUPT          = 0
HIGH_THRESHOLD_INTERRUPT         = 1
INTERRUPT_X_ENABLE               = 0
INTERRUPT_Y_ENABLE               = 0
INTERRUPT_Z_ENABLE               = 0
INTERRUPT_X_DISABLE              = 1
INTERRUPT_Y_DISABLE              = 1
INTERRUPT_Z_DISABLE              = 1
ENABLE_INTERRUPT_PIN             = 1
DISABLE_INTERRUPT_PIN            = 0
NO_DATA                          = -32768

# -------------------------------------------
BMM350_CHIP_ID_ERROR             = -1


# -------------------------------------------

BMM350_DISABLE_INTERRUPT = BMM350_DISABLE
BMM350_ENABLE_INTERRUPT = BMM350_ENABLE

BMM350_SUSPEND_MODE = BMM350_PMU_CMD_SUS
BMM350_NORMAL_MODE = BMM350_PMU_CMD_NM
BMM350_FORCED_MODE = BMM350_PMU_CMD_FM
BMM350_FORCED_MODE_FAST = BMM350_PMU_CMD_FM_FAST

BMM350_DATA_RATE_400HZ    = BMM350_ODR_400HZ
BMM350_DATA_RATE_200HZ    = BMM350_ODR_200HZ
BMM350_DATA_RATE_100HZ    = BMM350_ODR_100HZ
BMM350_DATA_RATE_50HZ     = BMM350_ODR_50HZ
BMM350_DATA_RATE_25HZ     = BMM350_ODR_25HZ
BMM350_DATA_RATE_12_5HZ   = BMM350_ODR_12_5HZ
BMM350_DATA_RATE_6_25HZ   = BMM350_ODR_6_25HZ
BMM350_DATA_RATE_3_125HZ  = BMM350_ODR_3_125HZ
BMM350_DATA_RATE_1_5625HZ = BMM350_ODR_1_5625HZ

BMM350_FLUXGUIDE_9MS = BMM350_PMU_CMD_FGR
BMM350_FLUXGUIDE_FAST = BMM350_PMU_CMD_FGR_FAST
BMM350_BITRESET_9MS = BMM350_PMU_CMD_BR
BMM350_BITRESET_FAST = BMM350_PMU_CMD_BR_FAST
BMM350_NOMAGRESET = 127

BMM350_INTR_DISABLE = BMM350_DISABLE
BMM350_INTR_ENABLE = BMM350_ENABLE

BMM350_UNMAP_FROM_PIN = BMM350_DISABLE
BMM350_MAP_TO_PIN = BMM350_ENABLE

BMM350_PULSED = BMM350_INT_MODE_PULSED
BMM350_LATCHED = BMM350_INT_MODE_LATCHED

BMM350_ACTIVE_LOW = BMM350_INT_POL_ACTIVE_LOW
BMM350_ACTIVE_HIGH = BMM350_INT_POL_ACTIVE_HIGH

BMM350_INTR_OPEN_DRAIN = BMM350_INT_OD_OPENDRAIN
BMM350_INTR_PUSH_PULL = BMM350_INT_OD_PUSHPULL

BMM350_IBI_DISABLE = BMM350_DISABLE
BMM350_IBI_ENABLE = BMM350_ENABLE

BMM350_NOCLEAR_ON_IBI = BMM350_DISABLE
BMM350_CLEAR_ON_IBI = BMM350_ENABLE

BMM350_I2C_WDT_DIS = BMM350_DISABLE
BMM350_I2C_WDT_EN = BMM350_ENABLE

BMM350_I2C_WDT_SEL_SHORT = BMM350_DISABLE
BMM350_I2C_WDT_SEL_LONG = BMM350_ENABLE

BMM350_NO_AVERAGING = BMM350_AVG_NO_AVG
BMM350_AVERAGING_2 = BMM350_AVG_2
BMM350_AVERAGING_4 = BMM350_AVG_4
BMM350_AVERAGING_8 = BMM350_AVG_8

BMM350_ST_IGEN_DIS = BMM350_DISABLE
BMM350_ST_IGEN_EN = BMM350_ENABLE

BMM350_ST_N_DIS = BMM350_DISABLE
BMM350_ST_N_EN = BMM350_ENABLE

BMM350_ST_P_DIS = BMM350_DISABLE
BMM350_ST_P_EN = BMM350_ENABLE

BMM350_IST_X_DIS = BMM350_DISABLE
BMM350_IST_X_EN = BMM350_ENABLE

BMM350_IST_Y_DIS = BMM350_DISABLE
BMM350_IST_Y_EN = BMM350_ENABLE

BMM350_CFG_SENS_TIM_AON_DIS = BMM350_DISABLE
BMM350_CFG_SENS_TIM_AON_EN = BMM350_ENABLE

BMM350_X_DIS = BMM350_DISABLE
BMM350_X_EN = BMM350_ENABLE

BMM350_Y_DIS = BMM350_DISABLE
BMM350_Y_EN = BMM350_ENABLE

BMM350_Z_DIS = BMM350_DISABLE
BMM350_Z_EN = BMM350_ENABLE

PI        = 3.141592653
M_PI	    = 3.14159265358979323846


# --------------------------------------------
'''!
  @brief bmm350 magnetometer dut offset coefficient structure
'''
class bmm350_dut_offset_coef:
    def __init__(self, t_offs: float, offset_x: float, offset_y: float, offset_z: float):
        self.t_offs = t_offs
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z

'''!
  @brief bmm350 magnetometer dut sensitivity coefficient structure
'''
class bmm350_dut_sensit_coef:
    def __init__(self, t_sens: float, sens_x: float, sens_y: float, sens_z: float):
        self.t_sens = t_sens
        self.sens_x = sens_x
        self.sens_y = sens_y
        self.sens_z = sens_z

'''!
  @brief bmm350 magnetometer dut tco structure
'''
class bmm350_dut_tco:
    def __init__(self, tco_x: float, tco_y: float, tco_z: float):
        self.tco_x = tco_x
        self.tco_y = tco_y
        self.tco_z = tco_z
'''!
  @brief bmm350 magnetometer dut tcs structure
'''
class bmm350_dut_tcs:
    def __init__(self, tcs_x: float, tcs_y: float, tcs_z: float):
        self.tcs_x = tcs_x
        self.tcs_y = tcs_y
        self.tcs_z = tcs_z

'''!
  @brief bmm350 magnetometer cross axis compensation structure
'''
class bmm350_cross_axis:
    def __init__(self, cross_x_y: float, cross_y_x: float, cross_z_x: float, cross_z_y: float):
        self.cross_x_y = cross_x_y
        self.cross_y_x = cross_y_x
        self.cross_z_x = cross_z_x
        self.cross_z_y = cross_z_y

'''!
  @brief bmm350 magnetometer compensate structure
'''
class bmm350_mag_compensate:
    def __init__(self, dut_offset_coef: bmm350_dut_offset_coef, dut_sensit_coef: bmm350_dut_sensit_coef, dut_tco: bmm350_dut_tco, dut_tcs: bmm350_dut_tcs, dut_t0: float, cross_axis: bmm350_cross_axis):
        self.dut_offset_coef = dut_offset_coef
        self.dut_sensit_coef = dut_sensit_coef
        self.dut_tco = dut_tco
        self.dut_tcs = dut_tcs
        self.dut_t0 = dut_t0
        self.cross_axis = cross_axis

'''!
  @brief bmm350 device structure
'''
class bmm350_dev:
  def __init__(self, mag_comp: bmm350_mag_compensate):
    self.chipID   = 0
    self.otp_data = [0] * 32
    self.var_id = 0
    self.mag_comp = mag_comp
    self.power_mode = 0
    self.axis_en = 0

# Create instances of the required classes with example values
dut_offset_coef = bmm350_dut_offset_coef(t_offs=0, offset_x=0, offset_y=0, offset_z=0)
dut_sensit_coef = bmm350_dut_sensit_coef(t_sens=0, sens_x=0, sens_y=0, sens_z=0)
dut_tco = bmm350_dut_tco(tco_x=0, tco_y=0, tco_z=0)
dut_tcs = bmm350_dut_tcs(tcs_x=0, tcs_y=0, tcs_z=0)
cross_axis = bmm350_cross_axis(cross_x_y=0, cross_y_x=0, cross_z_x=0, cross_z_y=0)
mag_comp = bmm350_mag_compensate(
    dut_offset_coef=dut_offset_coef,
    dut_sensit_coef=dut_sensit_coef,
    dut_tco=dut_tco,
    dut_tcs=dut_tcs,
    dut_t0=0,
    cross_axis=cross_axis
)
# The bmm350_mag_compensate object now contains all the data defined above.
bmm350_sensor = bmm350_dev(mag_comp)


# Uncompensated geomagnetic and temperature data
class BMM350RawMagData:
  def __init__(self):
    self.raw_x_data = 0
    self.raw_y_data = 0
    self.raw_z_data = 0
    self.raw_t_data = 0
_raw_mag_data = BMM350RawMagData()

class BMM350MagData:
  def __init__(self):
    self.x  = 0
    self.y  = 0
    self.z  = 0
    self.temperature  = 0
_mag_data = BMM350MagData()

class bmm350_pmu_cmd_status_0:
    def __init__(self, pmu_cmd_busy, odr_ovwr, avr_ovwr, pwr_mode_is_normal, cmd_is_illegal, pmu_cmd_value):
        self.pmu_cmd_busy = pmu_cmd_busy
        self.odr_ovwr = odr_ovwr
        self.avr_ovwr = avr_ovwr
        self.pwr_mode_is_normal = pwr_mode_is_normal
        self.cmd_is_illegal = cmd_is_illegal
        self.pmu_cmd_value = pmu_cmd_value
pmu_cmd_stat_0 = bmm350_pmu_cmd_status_0(pmu_cmd_busy=0, odr_ovwr=0, avr_ovwr=0, pwr_mode_is_normal=0, cmd_is_illegal=0, pmu_cmd_value=0)

# --------------------------------------------
class DFRobot_bmm350(object):
  I2C_MODE                       = 1
  I3C_MODE                       = 2
  __thresholdMode = 2
  threshold = 0


  def __init__(self, bus):
    if bus != 0:
      self.__i2c_i3c = self.I2C_MODE
    else:
      self.__i2c_i3c = self.I3C_MODE

  def BMM350_SET_BITS(self, reg_data, bitname_msk, bitname_pos, data):
    return (reg_data & ~bitname_msk) | ((data << bitname_pos) & bitname_msk)

  def BMM350_GET_BITS(self, reg_data, mask, pos):
    return (reg_data & mask) >> pos
 
  def BMM350_GET_BITS_POS_0(self, reg_data, mask):
    return reg_data & mask

  def BMM350_SET_BITS_POS_0(self, reg_data, mask, data):
    return ((reg_data & ~(mask)) | (data & mask))  



  # brief This internal API converts the raw data from the IC data registers to signed integer
  def fix_sign(self, inval, number_of_bits):
    power = 0
    if number_of_bits == BMM350_SIGNED_8_BIT:
      power = 128; # 2^7
    elif number_of_bits == BMM350_SIGNED_12_BIT:
      power = 2048 # 2^11
    elif number_of_bits == BMM350_SIGNED_16_BIT:
      power = 32768 # 2^15
    elif number_of_bits == BMM350_SIGNED_21_BIT:
      power = 1048576 # 2^20
    elif number_of_bits == BMM350_SIGNED_24_BIT:
      power = 8388608 # 2^23
    else:
      power = 0
    if inval >= power:
      inval = inval - (power * 2)
    return inval

  # brief This internal API is used to update magnetometer offset and sensitivity data.
  def update_mag_off_sens(self):
    off_x_lsb_msb = bmm350_sensor.otp_data[BMM350_MAG_OFFSET_X] & 0x0FFF
    off_y_lsb_msb = ((bmm350_sensor.otp_data[BMM350_MAG_OFFSET_X] & 0xF000) >> 4) + (bmm350_sensor.otp_data[BMM350_MAG_OFFSET_Y] & BMM350_LSB_MASK)
    off_z_lsb_msb = (bmm350_sensor.otp_data[BMM350_MAG_OFFSET_Y] & 0x0F00) + (bmm350_sensor.otp_data[BMM350_MAG_OFFSET_Z] & BMM350_LSB_MASK)
    t_off = bmm350_sensor.otp_data[BMM350_TEMP_OFF_SENS] & BMM350_LSB_MASK

    bmm350_sensor.mag_comp.dut_offset_coef.offset_x = self.fix_sign(off_x_lsb_msb, BMM350_SIGNED_12_BIT)
    bmm350_sensor.mag_comp.dut_offset_coef.offset_y = self.fix_sign(off_y_lsb_msb, BMM350_SIGNED_12_BIT)
    bmm350_sensor.mag_comp.dut_offset_coef.offset_z = self.fix_sign(off_z_lsb_msb, BMM350_SIGNED_12_BIT)
    bmm350_sensor.mag_comp.dut_offset_coef.t_offs = self.fix_sign(t_off, BMM350_SIGNED_8_BIT) / 5.0

    sens_x = (bmm350_sensor.otp_data[BMM350_MAG_SENS_X] & BMM350_MSB_MASK) >> 8
    sens_y = (bmm350_sensor.otp_data[BMM350_MAG_SENS_Y] & BMM350_LSB_MASK)
    sens_z = (bmm350_sensor.otp_data[BMM350_MAG_SENS_Z] & BMM350_MSB_MASK) >> 8
    t_sens = (bmm350_sensor.otp_data[BMM350_TEMP_OFF_SENS] & BMM350_MSB_MASK) >> 8

    bmm350_sensor.mag_comp.dut_sensit_coef.sens_x = self.fix_sign(sens_x, BMM350_SIGNED_8_BIT) / 256.0
    bmm350_sensor.mag_comp.dut_sensit_coef.sens_y = (self.fix_sign(sens_y, BMM350_SIGNED_8_BIT) / 256.0) + BMM350_SENS_CORR_Y
    bmm350_sensor.mag_comp.dut_sensit_coef.sens_z = self.fix_sign(sens_z, BMM350_SIGNED_8_BIT) / 256.0
    bmm350_sensor.mag_comp.dut_sensit_coef.t_sens = self.fix_sign(t_sens, BMM350_SIGNED_8_BIT) / 512.0

    tco_x = (bmm350_sensor.otp_data[BMM350_MAG_TCO_X] & BMM350_LSB_MASK)
    tco_y = (bmm350_sensor.otp_data[BMM350_MAG_TCO_Y] & BMM350_LSB_MASK)
    tco_z = (bmm350_sensor.otp_data[BMM350_MAG_TCO_Z] & BMM350_LSB_MASK)

    bmm350_sensor.mag_comp.dut_tco.tco_x = self.fix_sign(tco_x, BMM350_SIGNED_8_BIT) / 32.0
    bmm350_sensor.mag_comp.dut_tco.tco_y = self.fix_sign(tco_y, BMM350_SIGNED_8_BIT) / 32.0
    bmm350_sensor.mag_comp.dut_tco.tco_z = self.fix_sign(tco_z, BMM350_SIGNED_8_BIT) / 32.0

    tcs_x = (bmm350_sensor.otp_data[BMM350_MAG_TCS_X] & BMM350_MSB_MASK) >> 8
    tcs_y = (bmm350_sensor.otp_data[BMM350_MAG_TCS_Y] & BMM350_MSB_MASK) >> 8
    tcs_z = (bmm350_sensor.otp_data[BMM350_MAG_TCS_Z] & BMM350_MSB_MASK) >> 8

    bmm350_sensor.mag_comp.dut_tcs.tcs_x = self.fix_sign(tcs_x, BMM350_SIGNED_8_BIT) / 16384.0
    bmm350_sensor.mag_comp.dut_tcs.tcs_y = self.fix_sign(tcs_y, BMM350_SIGNED_8_BIT) / 16384.0
    bmm350_sensor.mag_comp.dut_tcs.tcs_z = (self.fix_sign(tcs_z, BMM350_SIGNED_8_BIT) / 16384.0) - BMM350_TCS_CORR_Z

    bmm350_sensor.mag_comp.dut_t0 = (self.fix_sign(bmm350_sensor.otp_data[BMM350_MAG_DUT_T_0], BMM350_SIGNED_16_BIT) / 512.0) + 23.0

    cross_x_y = (bmm350_sensor.otp_data[BMM350_CROSS_X_Y] & BMM350_LSB_MASK)
    cross_y_x = (bmm350_sensor.otp_data[BMM350_CROSS_Y_X] & BMM350_MSB_MASK) >> 8
    cross_z_x = (bmm350_sensor.otp_data[BMM350_CROSS_Z_X] & BMM350_LSB_MASK)
    cross_z_y = (bmm350_sensor.otp_data[BMM350_CROSS_Z_Y] & BMM350_MSB_MASK) >> 8

    bmm350_sensor.mag_comp.cross_axis.cross_x_y = self.fix_sign(cross_x_y, BMM350_SIGNED_8_BIT) / 800.0
    bmm350_sensor.mag_comp.cross_axis.cross_y_x = self.fix_sign(cross_y_x, BMM350_SIGNED_8_BIT) / 800.0
    bmm350_sensor.mag_comp.cross_axis.cross_z_x = self.fix_sign(cross_z_x, BMM350_SIGNED_8_BIT) / 800.0
    bmm350_sensor.mag_comp.cross_axis.cross_z_y = self.fix_sign(cross_z_y, BMM350_SIGNED_8_BIT) / 800.0


  def bmm350_set_powermode(self, powermode):
    last_pwr_mode = self.read_reg(BMM350_REG_PMU_CMD, 1)
    if (last_pwr_mode[0] == BMM350_PMU_CMD_NM) or (last_pwr_mode[0] == BMM350_PMU_CMD_UPD_OAE):
      self.write_reg(BMM350_REG_PMU_CMD, BMM350_PMU_CMD_SUS)
      time.sleep(BMM350_GOTO_SUSPEND_DELAY)
    # Array to store suspend to forced mode delay
    sus_to_forced_mode =[BMM350_SUS_TO_FORCEDMODE_NO_AVG_DELAY, BMM350_SUS_TO_FORCEDMODE_AVG_2_DELAY, 
                          BMM350_SUS_TO_FORCEDMODE_AVG_4_DELAY, BMM350_SUS_TO_FORCEDMODE_AVG_8_DELAY]
    # Array to store suspend to forced mode fast delay
    sus_to_forced_mode_fast = [BMM350_SUS_TO_FORCEDMODE_FAST_NO_AVG_DELAY, BMM350_SUS_TO_FORCEDMODE_FAST_AVG_2_DELAY,
                               BMM350_SUS_TO_FORCEDMODE_FAST_AVG_4_DELAY, BMM350_SUS_TO_FORCEDMODE_FAST_AVG_8_DELAY]
    # Set PMU command configuration to desired power mode
    self.write_reg(BMM350_REG_PMU_CMD, powermode)
    # Get average configuration
    get_avg = self.read_reg(BMM350_REG_PMU_CMD_AGGR_SET, 1)
    # Mask the average value
    avg = ((get_avg[0] & BMM350_AVG_MSK) >> BMM350_AVG_POS)
    delay_us = 0
    # Check if desired power mode is normal mode
    if powermode == BMM350_NORMAL_MODE:
      delay_us = BMM350_SUSPEND_TO_NORMAL_DELAY
    # Check if desired power mode is forced mode
    if powermode == BMM350_FORCED_MODE:
      delay_us = sus_to_forced_mode[avg]; # Store delay based on averaging mode
    # Check if desired power mode is forced mode fast
    if powermode == BMM350_FORCED_MODE_FAST:
        delay_us = sus_to_forced_mode_fast[avg] # Store delay based on averaging mode
    # Perform delay based on power mode
    time.sleep(delay_us)
    bmm350_sensor.power_mode = powermode


  def bmm350_magnetic_reset_and_wait(self):
    # 1. Read PMU CMD status
    reg_data = self.read_reg(BMM350_REG_PMU_CMD_STATUS_0, 1)
    pmu_cmd_stat_0.pmu_cmd_busy = self.BMM350_GET_BITS_POS_0(reg_data[0], BMM350_PMU_CMD_BUSY_MSK)
    pmu_cmd_stat_0.odr_ovwr = self.BMM350_GET_BITS(reg_data[0], BMM350_ODR_OVWR_MSK, BMM350_ODR_OVWR_POS)
    pmu_cmd_stat_0.avr_ovwr = self.BMM350_GET_BITS(reg_data[0], BMM350_AVG_OVWR_MSK, BMM350_AVG_OVWR_POS)
    pmu_cmd_stat_0.pwr_mode_is_normal = self.BMM350_GET_BITS(reg_data[0], BMM350_PWR_MODE_IS_NORMAL_MSK, BMM350_PWR_MODE_IS_NORMAL_POS)
    pmu_cmd_stat_0.cmd_is_illegal = self.BMM350_GET_BITS(reg_data[0], BMM350_CMD_IS_ILLEGAL_MSK, BMM350_CMD_IS_ILLEGAL_POS)
    pmu_cmd_stat_0.pmu_cmd_value = self.BMM350_GET_BITS(reg_data[0], BMM350_PMU_CMD_VALUE_MSK, BMM350_PMU_CMD_VALUE_POS)
    # 2. Check whether the power mode is normal before magnetic reset
    restore_normal = BMM350_DISABLE
    if pmu_cmd_stat_0.pwr_mode_is_normal == BMM350_ENABLE:
      restore_normal = BMM350_ENABLE
    # Reset can only be triggered in suspend
    self.bmm350_set_powermode(BMM350_SUSPEND_MODE)
    # Set BR to PMU_CMD register
    self.write_reg(BMM350_REG_PMU_CMD, BMM350_PMU_CMD_BR)
    time.sleep(BMM350_BR_DELAY)
    # Set FGR to PMU_CMD register
    self.write_reg(BMM350_REG_PMU_CMD, BMM350_PMU_CMD_FGR)
    time.sleep(BMM350_FGR_DELAY)
    if restore_normal == BMM350_ENABLE:
      self.bmm350_set_powermode(BMM350_NORMAL_MODE)


  def sensor_init(self):
    '''!
      @brief Init bmm350 check whether the chip id is right
      @return 
      @retval 0  is init success
      @retval -1 is init failed
    '''
    rslt = BMM350_OK
    # Specifies that all axes are enabled
    bmm350_sensor.axis_en = BMM350_EN_XYZ_MSK
    time.sleep(BMM350_START_UP_TIME_FROM_POR)
    # 1. Software reset
    self.write_reg(BMM350_REG_CMD, BMM350_CMD_SOFTRESET)
    time.sleep(BMM350_SOFT_RESET_DELAY)
    # 2. Read chip ID
    reg_date = self.read_reg(BMM350_REG_CHIP_ID, 1)
    bmm350_sensor.chipID = reg_date[0]
    if reg_date[0] == BMM350_CHIP_ID:
      # 3. Download OTP compensation data
      for indx in range(BMM350_OTP_DATA_LENGTH):
        # 3.1 Set the OTP address register -- > Each address corresponds to a different OTP value (total OTP data is 32 bytes)
        otp_cmd = BMM350_OTP_CMD_DIR_READ | (indx & BMM350_OTP_WORD_ADDR_MSK)
        self.write_reg(BMM350_REG_OTP_CMD_REG, otp_cmd)
        while (True):
          time.sleep(0.0003)
          # 3.2 The OTP status was read
          otp_status = self.read_reg(BMM350_REG_OTP_STATUS_REG, 1)
          otp_err = otp_status[0] & BMM350_OTP_STATUS_ERROR_MSK
          if otp_err != BMM350_OTP_STATUS_NO_ERROR:
            break
          if (otp_status[0] & BMM350_OTP_STATUS_CMD_DONE):
            break
        # 3.3 Gets 16 bytes of OTP data from the OTP address specified above
        OTP_MSB_data = self.read_reg(BMM350_REG_OTP_DATA_MSB_REG, 1)
        OTP_LSB_data = self.read_reg(BMM350_REG_OTP_DATA_LSB_REG, 1)
        OTP_data = ((OTP_MSB_data[0] << 8) | OTP_LSB_data[0]) & 0xFFFF
        bmm350_sensor.otp_data[indx] = OTP_data
        bmm350_sensor.var_id = (bmm350_sensor.otp_data[30] & 0x7f00) >> 9
        # 3.4 Update the magnetometer offset and sensitivity data
        self.update_mag_off_sens()
      # 4. Disable OTP
      self.write_reg(BMM350_REG_OTP_CMD_REG, BMM350_OTP_CMD_PWR_OFF_OTP)

      # 5. Magnetic reset
      self.bmm350_magnetic_reset_and_wait()
    else:
      # The chip id verification failed and initialization failed. Procedure
      rslt = BMM350_CHIP_ID_ERROR
    return rslt


  def get_chip_id(self):
    chip_id = self.read_reg(BMM350_REG_CHIP_ID, 1)
    return chip_id[0]


  def soft_reset(self):
    '''!
      @brief Soft reset, restore to suspended mode after soft reset. (You need to manually enter the normal mode)
    '''
    self.write_reg(BMM350_REG_CMD, BMM350_CMD_SOFTRESET) # Software reset
    time.sleep(BMM350_SOFT_RESET_DELAY)
    self.write_reg(BMM350_REG_OTP_CMD_REG, BMM350_OTP_CMD_PWR_OFF_OTP) # Disable OTP
    self.bmm350_magnetic_reset_and_wait() # magnetic reset
    self.bmm350_set_powermode(BMM350_SUSPEND_MODE)


  def set_operation_mode(self, modes):
    '''!
      @brief Set sensor operation mode
      @param modes
      @n BMM350_SUSPEND_MODE      suspend mode: Suspend mode is the default power mode of BMM350 after the chip is powered, Current consumption in suspend mode is minimal, 
                                  so, this mode is useful for periods when data conversion is not needed. Read and write of all registers is possible.
      @n BMM350_NORMAL_MODE       normal mode: Get geomagnetic data normally.      
      @n BMM350_FORCED_MODE       forced mode: Single measurement, the sensor restores to suspend mode when the measurement is done.
      @n BMM350_FORCED_MODE_FAST  To reach ODR = 200Hz is only possible by using FM_ FAST.
    '''
    self.bmm350_set_powermode(modes)


  def get_operation_mode(self):
    '''!
      @brief Get sensor operation mode
      @return Return the character string of the operation mode
    '''
    result = ""
    if bmm350_sensor.power_mode == BMM350_SUSPEND_MODE:
       result = "bmm350 is suspend mode!"
    elif bmm350_sensor.power_mode == BMM350_NORMAL_MODE:
       result = "bmm350 is normal mode!"
    elif bmm350_sensor.power_mode == BMM350_FORCED_MODE:
       result = "bmm350 is forced mode!"
    elif bmm350_sensor.power_mode == BMM350_FORCED_MODE_FAST:
       result = "bmm350 is forced_fast mode!"
    else:
       result = "error mode!"
    return result





  def get_rate(self):
    '''!
      @brief Get the config data rate, unit: HZ
      @return rate
    '''
    avg_odr_reg = self.read_reg(BMM350_REG_PMU_CMD_AGGR_SET, 1)
    odr_reg = self.BMM350_GET_BITS(avg_odr_reg[0], BMM350_ODR_MSK, BMM350_ODR_POS)
    if odr_reg == BMM350_ODR_1_5625HZ:
      result = 1.5625
    elif odr_reg == BMM350_ODR_3_125HZ:
      result = 3.125
    elif odr_reg == BMM350_ODR_6_25HZ:
      result = 6.25
    elif odr_reg == BMM350_ODR_12_5HZ:
      result = 12.5
    elif odr_reg == BMM350_ODR_25HZ:
      result = 25
    elif odr_reg == BMM350_ODR_50HZ:
      result = 50
    elif odr_reg == BMM350_ODR_100HZ:
      result = 100
    elif odr_reg == BMM350_ODR_200HZ:
      result = 200
    elif odr_reg == BMM350_ODR_400HZ:
      result = 400
    return result


  def set_preset_mode(self, avg, rate = BMM350_DATA_RATE_12_5HZ):
    '''!
      @brief Set preset mode, make it easier for users to configure sensor to get geomagnetic data (The default rate for obtaining geomagnetic data is 12.5Hz)
      @param modes 
      @n BMM350_PRESETMODE_LOWPOWER       Low power mode, get a fraction of data and take the mean value.
      @n BMM350_PRESETMODE_REGULAR        Regular mode, get a number of data and take the mean value.
      @n BMM350_PRESETMODE_ENHANCED       Enhanced mode, get a plenty of data and take the mean value.
      @n BMM350_PRESETMODE_HIGHACCURACY   High accuracy mode, get a huge number of data and take the mean value.
      @param rate
      @n BMM350_DATA_RATE_1_5625HZ
      @n BMM350_DATA_RATE_3_125HZ
      @n BMM350_DATA_RATE_6_25HZ
      @n BMM350_DATA_RATE_12_5HZ  (default rate)
      @n BMM350_DATA_RATE_25HZ
      @n BMM350_DATA_RATE_50HZ
      @n BMM350_DATA_RATE_100HZ
      @n BMM350_DATA_RATE_200HZ
      @n BMM350_DATA_RATE_400HZ

    '''
    reg_data = (rate & BMM350_ODR_MSK)
    reg_data = self.BMM350_SET_BITS(reg_data, BMM350_AVG_MSK, BMM350_AVG_POS, avg)
    self.write_reg(BMM350_REG_PMU_CMD_AGGR_SET, reg_data)
    self.write_reg(BMM350_REG_PMU_CMD, BMM350_PMU_CMD_UPD_OAE)  

  def set_rate(self, rates):
    '''!
      @brief Set the rate of obtaining geomagnetic data, the higher, the faster (without delay function)
      @param rate
      @n BMM350_DATA_RATE_1_5625HZ
      @n BMM350_DATA_RATE_3_125HZ
      @n BMM350_DATA_RATE_6_25HZ
      @n BMM350_DATA_RATE_12_5HZ  (default rate)
      @n BMM350_DATA_RATE_25HZ
      @n BMM350_DATA_RATE_50HZ
      @n BMM350_DATA_RATE_100HZ
      @n BMM350_DATA_RATE_200HZ
      @n BMM350_DATA_RATE_400HZ
    '''
    # self.bmm350_set_powermode(BMM350_NORMAL_MODE)
    avg_odr_reg = self.read_reg(BMM350_REG_PMU_CMD_AGGR_SET, 1)
    avg_reg = self.BMM350_GET_BITS(avg_odr_reg[0], BMM350_AVG_MSK, BMM350_AVG_POS)
    reg_data = (rates & BMM350_ODR_MSK)
    reg_data = self.BMM350_SET_BITS(reg_data, BMM350_AVG_MSK, BMM350_AVG_POS, avg_reg)
    self.write_reg(BMM350_REG_PMU_CMD_AGGR_SET, reg_data)
    self.write_reg(BMM350_REG_PMU_CMD, BMM350_PMU_CMD_UPD_OAE)
    time.sleep(BMM350_UPD_OAE_DELAY)
    
  def self_test(self):
    '''!
      @brief Sensor self test, the returned character string indicate the self test result.
      @return The character string of the test result
    '''
    axis_en = self.read_reg(BMM350_REG_PMU_CMD_AXIS_EN, 1)
    en_x = self.BMM350_GET_BITS(axis_en[0], BMM350_EN_X_MSK, BMM350_EN_X_POS)
    en_y = self.BMM350_GET_BITS(axis_en[0], BMM350_EN_Y_MSK, BMM350_EN_Y_POS)
    en_z = self.BMM350_GET_BITS(axis_en[0], BMM350_EN_Z_MSK, BMM350_EN_Z_POS)
    str1 = ""
    if en_x & 0x01:
      str1 += "x "
    if en_y & 0x01:
      str1 += "y "
    if en_z & 0x01:
      str1 += "z "
    if axis_en == 0:
      str1 = "xyz aix self test fail"
    else:
      str1 += "aix test success"
    return str1


  def set_measurement_XYZ(self, en_x = BMM350_X_EN, en_y = BMM350_Y_EN, en_z = BMM350_Z_EN):
    '''!
      @brief Enable the measurement at x-axis, y-axis and z-axis, default to be enabled. After disabling, the geomagnetic data at x, y, and z axis are wrong.
      @param en_x
      @n   BMM350_X_EN        Enable the measurement at x-axis
      @n   BMM350_X_DIS       Disable the measurement at x-axis
      @param en_y
      @n   BMM350_Y_EN        Enable the measurement at y-axis
      @n   BMM350_Y_DIS       Disable the measurement at y-axis
      @param en_z
      @n   BMM350_Z_EN        Enable the measurement at z-axis
      @n   BMM350_Z_DIS       Disable the measurement at z-axis
    '''
    if en_x == BMM350_X_DIS and en_y == BMM350_Y_DIS and en_z == BMM350_Z_DIS:
      bmm350_sensor.axis_en = BMM350_DISABLE
    else:
      axis_en = self.read_reg(BMM350_REG_PMU_CMD_AXIS_EN, 1)
      data = self.BMM350_SET_BITS(axis_en[0], BMM350_EN_X_MSK, BMM350_EN_X_POS, en_x)
      data = self.BMM350_SET_BITS(data, BMM350_EN_Y_MSK, BMM350_EN_Y_POS, en_y)
      data = self.BMM350_SET_BITS(data, BMM350_EN_Z_MSK, BMM350_EN_Z_POS, en_z)
      bmm350_sensor.axis_en = data


  def get_measurement_state_XYZ(self):
    '''!
      @brief Get the enabling status at x-axis, y-axis and z-axis
      @return Return enabling status at x-axis, y-axis and z-axis as a character string
    '''
    axis_en = bmm350_sensor.axis_en
    en_x = self.BMM350_GET_BITS(axis_en, BMM350_EN_X_MSK, BMM350_EN_X_POS)
    en_y = self.BMM350_GET_BITS(axis_en, BMM350_EN_Y_MSK, BMM350_EN_Y_POS)
    en_z = self.BMM350_GET_BITS(axis_en, BMM350_EN_Z_MSK, BMM350_EN_Z_POS)
    result = ""
    result += "The x axis is enable! " if en_x == 1 else "The x axis is disable! "
    result += "The y axis is enable! " if en_y == 1 else "The y axis is disable! "
    result += "The z axis is enable! " if en_z == 1 else "The z axis is disable! "
    return result


  def  get_geomagnetic_data(self):
    '''!
      @brief Get the geomagnetic data of 3 axis (x, y, z)
      @return The list of the geomagnetic data at 3 axis (x, y, z) unit: uT
      @       [0] The geomagnetic data at x-axis
      @       [1] The geomagnetic data at y-axis
      @       [2] The geomagnetic data at z-axis
    '''
    # 1. Get raw data without compensation
    mag_data = self.read_reg(BMM350_REG_MAG_X_XLSB, BMM350_MAG_TEMP_DATA_LEN)
    raw_mag_x = mag_data[0] + (mag_data[1] << 8) + (mag_data[2] << 16)
    raw_mag_y = mag_data[3] + (mag_data[4] << 8) + (mag_data[5] << 16)
    raw_mag_z = mag_data[6] + (mag_data[7] << 8) + (mag_data[8] << 16)
    raw_temp = mag_data[9] + (mag_data[10] << 8) + (mag_data[11] << 16)
    if (bmm350_sensor.axis_en & BMM350_EN_X_MSK) == BMM350_DISABLE:
      _raw_mag_data.raw_x_data = BMM350_DISABLE
    else:
      _raw_mag_data.raw_x_data = self.fix_sign(raw_mag_x, BMM350_SIGNED_24_BIT)
    if (bmm350_sensor.axis_en & BMM350_EN_Y_MSK) == BMM350_DISABLE:
      _raw_mag_data.raw_y_data = BMM350_DISABLE
    else:
      _raw_mag_data.raw_y_data = self.fix_sign(raw_mag_y, BMM350_SIGNED_24_BIT)
    if (bmm350_sensor.axis_en & BMM350_EN_Z_MSK) == BMM350_DISABLE:
      _raw_mag_data.raw_z_data = BMM350_DISABLE
    else:
      _raw_mag_data.raw_z_data = self.fix_sign(raw_mag_z, BMM350_SIGNED_24_BIT)
    _raw_mag_data.raw_t_data = self.fix_sign(raw_temp, BMM350_SIGNED_24_BIT)
    # 2. The raw data is processed
    # 2.1 Parameter preparation
    bxy_sens = 14.55
    bz_sens = 9.0
    temp_sens = 0.00204
    ina_xy_gain_trgt = 19.46
    ina_z_gain_trgt = 31.0
    adc_gain = 1 / 1.5
    lut_gain = 0.714607238769531
    power = (1000000.0 / 1048576.0)
    lsb_to_ut_degc = [None] * 4
    lsb_to_ut_degc[0] = (power / (bxy_sens * ina_xy_gain_trgt * adc_gain * lut_gain))
    lsb_to_ut_degc[1] = (power / (bxy_sens * ina_xy_gain_trgt * adc_gain * lut_gain))
    lsb_to_ut_degc[2] = (power / (bz_sens * ina_z_gain_trgt * adc_gain * lut_gain))
    lsb_to_ut_degc[3] = 1 / (temp_sens * adc_gain * lut_gain * 1048576)
    # 2.1 Start processing raw data
    out_data =  [None] * 4
    out_data[0] = _raw_mag_data.raw_x_data * lsb_to_ut_degc[0]
    out_data[1] = _raw_mag_data.raw_y_data * lsb_to_ut_degc[1]
    out_data[2] = _raw_mag_data.raw_z_data * lsb_to_ut_degc[2]
    out_data[3] = _raw_mag_data.raw_t_data * lsb_to_ut_degc[3]
    if out_data[3] > 0.0:
      temp = out_data[3] - (1 * 25.49)
    elif out_data[3] < 0.0:
      temp = out_data[3] - (-1 * 25.49)
    else:
      temp = out_data[3]
    out_data[3] = temp
    # 3. Compensate for the original data
    # 3.1 Compensation for temperature data
    out_data[3] = (1 + bmm350_sensor.mag_comp.dut_sensit_coef.t_sens) * out_data[3] + bmm350_sensor.mag_comp.dut_offset_coef.t_offs
    # 3.2 Store the magnetic compensation data in a list
    dut_offset_coef = [None] * 3
    dut_offset_coef[0] = bmm350_sensor.mag_comp.dut_offset_coef.offset_x
    dut_offset_coef[1] = bmm350_sensor.mag_comp.dut_offset_coef.offset_y
    dut_offset_coef[2] = bmm350_sensor.mag_comp.dut_offset_coef.offset_z

    dut_sensit_coef = [None] * 3
    dut_sensit_coef[0] = bmm350_sensor.mag_comp.dut_sensit_coef.sens_x
    dut_sensit_coef[1] = bmm350_sensor.mag_comp.dut_sensit_coef.sens_y
    dut_sensit_coef[2] = bmm350_sensor.mag_comp.dut_sensit_coef.sens_z

    dut_tco = [None] * 3
    dut_tco[0] = bmm350_sensor.mag_comp.dut_tco.tco_x
    dut_tco[1] = bmm350_sensor.mag_comp.dut_tco.tco_y
    dut_tco[2] = bmm350_sensor.mag_comp.dut_tco.tco_z

    dut_tcs = [None] * 3
    dut_tcs[0] = bmm350_sensor.mag_comp.dut_tcs.tcs_x
    dut_tcs[1] = bmm350_sensor.mag_comp.dut_tcs.tcs_y
    dut_tcs[2] = bmm350_sensor.mag_comp.dut_tcs.tcs_z;     
    # 3.3 Compensation for magnetic data
    for indx in range(3):
        out_data[indx] *= 1 + dut_sensit_coef[indx]
        out_data[indx] += dut_offset_coef[indx]
        out_data[indx] += dut_tco[indx] * (out_data[3] - bmm350_sensor.mag_comp.dut_t0)
        out_data[indx] /= 1 + dut_tcs[indx] * (out_data[3] - bmm350_sensor.mag_comp.dut_t0)

    cr_ax_comp_x = (out_data[0] - bmm350_sensor.mag_comp.cross_axis.cross_x_y * out_data[1]) / \
                   (1 - bmm350_sensor.mag_comp.cross_axis.cross_y_x * bmm350_sensor.mag_comp.cross_axis.cross_x_y)
    cr_ax_comp_y = (out_data[1] - bmm350_sensor.mag_comp.cross_axis.cross_y_x * out_data[0]) / \
                   (1 - bmm350_sensor.mag_comp.cross_axis.cross_y_x * bmm350_sensor.mag_comp.cross_axis.cross_x_y)
    cr_ax_comp_z = (out_data[2] + (out_data[0] *
          (bmm350_sensor.mag_comp.cross_axis.cross_y_x * bmm350_sensor.mag_comp.cross_axis.cross_z_y - bmm350_sensor.mag_comp.cross_axis.cross_z_x) - out_data[1] *
          (bmm350_sensor.mag_comp.cross_axis.cross_z_y - bmm350_sensor.mag_comp.cross_axis.cross_x_y * bmm350_sensor.mag_comp.cross_axis.cross_z_x)) /
          (1 - bmm350_sensor.mag_comp.cross_axis.cross_y_x * bmm350_sensor.mag_comp.cross_axis.cross_x_y))

    out_data[0] = cr_ax_comp_x
    out_data[1] = cr_ax_comp_y
    out_data[2] = cr_ax_comp_z

    if (bmm350_sensor.axis_en & BMM350_EN_X_MSK) == BMM350_DISABLE:
      _mag_data.x = BMM350_DISABLE
    else:
      _mag_data.x = out_data[0]

    if (bmm350_sensor.axis_en & BMM350_EN_Y_MSK) == BMM350_DISABLE:
      _mag_data.y = BMM350_DISABLE
    else:
      _mag_data.y = out_data[1]

    if (bmm350_sensor.axis_en & BMM350_EN_Z_MSK) == BMM350_DISABLE:
      _mag_data.z = BMM350_DISABLE
    else:
      _mag_data.z = out_data[2]

    _mag_data.temperature = out_data[3]

    geomagnetic = [None] * 3
    geomagnetic[0] = _mag_data.x
    geomagnetic[1] = _mag_data.y
    geomagnetic[2] = _mag_data.z
    return geomagnetic


  def get_compass_degree(self):
    '''!
      @brief Get compass degree
      @return Compass degree (0° - 360°)  0° = North, 90° = East, 180° = South, 270° = West.
    '''
    magData = self.get_geomagnetic_data()
    compass = math.atan2(magData[0], magData[1])
    if compass < 0:
      compass += 2 * PI
    if compass > 2 * PI:
      compass -= 2 * PI
    return compass * 180 / M_PI


  def set_data_ready_pin(self, modes, polarity):
    '''!
      @brief Enable or disable data ready interrupt pin
      @n After enabling, the DRDY pin jump when there's data coming.
      @n After disabling, the DRDY pin will not jump when there's data coming.
      @n High polarity  active on high, the default is low level, which turns to high level when the interrupt is triggered.
      @n Low polarity   active on low, default is high level, which turns to low level when the interrupt is triggered.
      @param modes
      @n     BMM350_ENABLE_INTERRUPT        Enable DRDY
      @n     BMM350_DISABLE_INTERRUPT       Disable DRDY
      @param polarity
      @n     BMM350_ACTIVE_HIGH              High polarity
      @n     BMM350_ACTIVE_LOW               Low polarity
    '''
    # 1. Gets and sets the interrupt control configuration
    reg_data = self.read_reg(BMM350_REG_INT_CTRL, 1)
    reg_data[0] = self.BMM350_SET_BITS_POS_0(reg_data[0], BMM350_INT_MODE_MSK, BMM350_INT_MODE_PULSED)
    reg_data[0] = self.BMM350_SET_BITS(reg_data[0], BMM350_INT_POL_MSK, BMM350_INT_POL_POS, polarity)
    reg_data[0] = self.BMM350_SET_BITS(reg_data[0], BMM350_INT_OD_MSK, BMM350_INT_OD_POS, BMM350_INT_OD_PUSHPULL) 
    reg_data[0] = self.BMM350_SET_BITS(reg_data[0], BMM350_INT_OUTPUT_EN_MSK, BMM350_INT_OUTPUT_EN_POS, BMM350_MAP_TO_PIN)
    reg_data[0] = self.BMM350_SET_BITS(reg_data[0], BMM350_DRDY_DATA_REG_EN_MSK, BMM350_DRDY_DATA_REG_EN_POS, modes)
    # 2. Update interrupt control configuration
    self.write_reg(BMM350_REG_INT_CTRL, reg_data[0]) 


  def get_data_ready_state(self):
    '''!
      @brief Get data ready status, determine whether the data is ready
      @return status
      @n True  Data ready
      @n False Data is not ready
    '''
    int_status_reg = self.read_reg(BMM350_REG_INT_STATUS, 1) 
    drdy_status = self.BMM350_GET_BITS(int_status_reg[0], BMM350_DRDY_DATA_REG_MSK, BMM350_DRDY_DATA_REG_POS)
    if drdy_status & 0x01:
      return True
    else:
      return False


  def set_threshold_interrupt(self, modes, threshold, polarity):
    '''!
      @brief Set threshold interrupt, an interrupt is triggered when the geomagnetic value of a channel is beyond/below the threshold
      @n      High polarity   active on high level, the default is low level, which turns to high level when the interrupt is triggered.
      @n      Low polarity    active on low level, the default is high level, which turns to low level when the interrupt is triggered.
      @param modes
      @n     LOW_THRESHOLD_INTERRUPT       Low threshold interrupt mode
      @n     HIGH_THRESHOLD_INTERRUPT      High threshold interrupt mode
      @param  threshold
      @n     Threshold, default to expand 16 times, for example: under low threshold mode, if the threshold is set to be 1, actually the geomagnetic data below 16 will trigger an interrupt
      @param polarity
      @n     POLARITY_HIGH      High polarity
      @n     POLARITY_LOW       Low polarity
    '''
    if modes == LOW_THRESHOLD_INTERRUPT:
      self.__thresholdMode = LOW_THRESHOLD_INTERRUPT
      self.set_data_ready_pin(BMM350_ENABLE_INTERRUPT, polarity)
      self.threshold = threshold
    else:
      self.__thresholdMode = HIGH_THRESHOLD_INTERRUPT
      self.set_data_ready_pin(BMM350_ENABLE_INTERRUPT, polarity)
      self.threshold = threshold
    

  def get_threshold_data(self):
    '''!
      @brief Get the data that threshold interrupt occured
      @return Return the list for storing geomagnetic data, how the data at 3 axis influence interrupt status,
      @n      [0] The data triggering threshold at x-axis, when the data is NO_DATA, the interrupt is triggered.
      @n      [1] The data triggering threshold at y-axis, when the data is NO_DATA, the interrupt is triggered.
      @n      [2] The data triggering threshold at z-axis, when the data is NO_DATA, the interrupt is triggered.
    '''
    Data = [NO_DATA] * 3
    state = self.get_data_ready_state()
    if state == True:
      magData = self.get_geomagnetic_data()
      if self.__thresholdMode == LOW_THRESHOLD_INTERRUPT:
        if magData[0] < self.threshold*16:
          Data[0] = magData[0]
        if magData[1] < self.threshold*16:
          Data[1] = magData[1]
        if magData[2] < self.threshold*16:
          Data[2] = magData[2]
      elif self.__thresholdMode == HIGH_THRESHOLD_INTERRUPT:
        if magData[0] < self.threshold*16:
          Data[0] = magData[0]
        if magData[1] < self.threshold*16:
          Data[1] = magData[1]
        if magData[2] < self.threshold*16:
          Data[2] = magData[2]
    return Data

# I2C interface
class DFRobot_bmm350_I2C(DFRobot_bmm350):
  '''!
    @brief An example of an i2c interface module
  '''
  def __init__(self, bus, addr):
    self.bus = bus
    self.__addr = addr
    if self.is_raspberrypi():
      import smbus2
      self.i2cbus = smbus2.SMBus(bus)
    else:
      self.test_platform()
    super(DFRobot_bmm350_I2C, self).__init__(self.bus)

  def is_raspberrypi(self):
    import io
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

  def test_platform(self):
    import re
    import platform
    import subprocess
    where = platform.system()
    if where == "Linux":
        p = subprocess.Popen(['i2cdetect', '-l'], stdout=subprocess.PIPE,)
        for i in range(0, 25):
            line = str(p.stdout.readline())
            s = re.search("i2c-tiny-usb", line)
            if s:
                line = re.split(r'\W+', line)
                bus = int(line[2])
        import smbus
        self.i2cbus = smbus.SMBus(bus)
    elif where == "Windows":
        from i2c_mp_usb import I2C_MP_USB as SMBus
        self.i2cbus = SMBus()
    else:
        print("Platform not supported")  



  def write_reg(self, reg, data):
    '''!
      @brief writes data to a register
      @param reg register address
      @param data written data
    '''
    while 1:
      try:
        self.i2cbus.write_byte_data(self.__addr, reg, data)
        return
      except:
        print("please check connect w!")
        time.sleep(1)
        return
  
  def read_reg(self, reg ,len):
    '''!
      @brief read the data from the register
      @param reg register address
      @param len read data length
    '''
    while True:
      try:
        # Read data from I2C bus
        temp_buf = self.i2cbus.read_i2c_block_data(self.__addr, reg, len + BMM350_DUMMY_BYTES)
        # Copy data after dummy byte indices
        reg_data = temp_buf[BMM350_DUMMY_BYTES:]
        return reg_data  # Assuming this function is part of a larger method
      except Exception as e:
        time.sleep(1)
        print("please check connect r!")
