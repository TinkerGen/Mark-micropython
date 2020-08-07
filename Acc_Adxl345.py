from machine import I2C
import time

ADXL345_DEVICE = (0x53)

""" ------- Register names ------- """
ADXL345_DEVID           =0x00
ADXL345_RESERVED1       =0x01
ADXL345_THRESH_TAP      =0x1d
ADXL345_OFSX            =0x1e
ADXL345_OFSY            =0x1f
ADXL345_OFSZ            =0x20
ADXL345_DUR             =0x21
ADXL345_LATENT          =0x22
ADXL345_WINDOW          =0x23
ADXL345_THRESH_ACT      =0x24
ADXL345_THRESH_INACT    =0x25
ADXL345_TIME_INACT      =0x26
ADXL345_ACT_INACT_CTL   =0x27
ADXL345_THRESH_FF       =0x28
ADXL345_TIME_FF         =0x29
ADXL345_TAP_AXES        =0x2a
ADXL345_ACT_TAP_STATUS  =0x2b
ADXL345_BW_RATE         =0x2c
ADXL345_POWER_CTL       =0x2d
ADXL345_INT_ENABLE      =0x2e
ADXL345_INT_MAP         =0x2f
ADXL345_INT_SOURCE      =0x30
ADXL345_DATA_FORMAT     =0x31
ADXL345_DATAX0          =0x32
ADXL345_DATAX1          =0x33
ADXL345_DATAY0          =0x34
ADXL345_DATAY1          =0x35
ADXL345_DATAZ0          =0x36
ADXL345_DATAZ1          =0x37
ADXL345_FIFO_CTL        =0x38
ADXL345_FIFO_STATUS     =0x39

ADXL345_BW_1600         =0xF                 #  1111
ADXL345_BW_800          =0xE                 #  1110
ADXL345_BW_400          =0xD                 #  1101
ADXL345_BW_200          =0xC                 #  1100
ADXL345_BW_100          =0xB                 #  1011
ADXL345_BW_50           =0xA                 #  1010
ADXL345_BW_25           =0x9                 #  1001
ADXL345_BW_12           =0x8                 #  1000
ADXL345_BW_6            =0x7                 #  0111
ADXL345_BW_3            =0x6                 #  0110

"""
Interrupt PINs
INT1: 0
INT2: 1
"""
ADXL345_INT1_PIN            =0x00
ADXL345_INT2_PIN            =0x01

"""Interrupt bit position"""
ADXL345_INT_DATA_READY_BIT  =0x07
ADXL345_INT_SINGLE_TAP_BIT  =0x06
ADXL345_INT_DOUBLE_TAP_BIT  =0x05
ADXL345_INT_ACTIVITY_BIT    =0x04
ADXL345_INT_INACTIVITY_BIT  =0x03
ADXL345_INT_FREE_FALL_BIT   =0x02
ADXL345_INT_WATERMARK_BIT   =0x01
ADXL345_INT_OVERRUNY_BIT    =0x00

ADXL345_DATA_READY          =0x07
ADXL345_SINGLE_TAP          =0x06
ADXL345_DOUBLE_TAP          =0x05
ADXL345_ACTIVITY            =0x04
ADXL345_INACTIVITY          =0x03
ADXL345_FREE_FALL           =0x02
ADXL345_WATERMARK           =0x01
ADXL345_OVERRUNY            =0x00

ADXL345_OK                  =1                   #  no error
ADXL345_ERROR               =0                   #  indicates error is predent

ADXL345_NO_ERROR            =0                   #  initial state
ADXL345_READ_ERROR          =1                   #  problem reading accel
ADXL345_BAD_ARG             =2                   #  bad method argument


class AccelerationAdxl345(object):

    def __init__(self, addr=ADXL345_DEVICE, drdy=None):
        self.i2c_device = I2C(I2C.I2C0, freq=100000, scl=30, sda=31)
        time.sleep(0.1)
        #self.rgbMatrixData = [0xFF]*64

    def read(self, reg_base, reg, buf):
        self.write(reg)
        time.sleep(.001)
        self.i2c_device.readfrom_into(59,buf)

    def write(self, buf=None):
        if buf is not None:
            self.i2c_device.writeto(ADXL345_DEVICE, buf)
        # i2c_device.writeto(0x58, bytearray([3,100,100,16,39]))

    def writeTo(self,address, val):
        dta_send = bytearray([address, val])
        self.write(dta_send)
    
    def readFrom(self, address, num):
        data_0 = address & 0xff
        dta_send = bytearray([data_0])
        self.write(dta_send)
        time.sleep(.001)
        result=self.i2c_device.readfrom(ADXL345_DEVICE, num)
        return result

    def setRegisterBit(self, regAdress,  bitPos,  state):  
        bytes=self.readFrom(regAdress, 1)
        for _b in bytes:
            value = int(_b)
        if (state):
            value |= (1 << bitPos)                 
        else:
            value &= ~(1 << bitPos)                   
        self.writeTo(regAdress, value)

    def acc_adxl345_init(self):
        #Turning on the ADXL345
        self.writeTo(ADXL345_POWER_CTL, 0)
        self.writeTo(ADXL345_POWER_CTL, 16)
        self.writeTo(ADXL345_POWER_CTL, 8)

        self.writeTo(ADXL345_THRESH_ACT, 75)
        self.writeTo(ADXL345_THRESH_INACT, 75)
        self.writeTo(ADXL345_TIME_INACT, 10)

        #look of activity movement on this axes - 1 == on; 0 == off
        self.setRegisterBit(ADXL345_ACT_INACT_CTL, 6, 1)
        self.setRegisterBit(ADXL345_ACT_INACT_CTL, 5, 1)
        self.setRegisterBit(ADXL345_ACT_INACT_CTL, 4, 1)

        #look of inactivity movement on this axes - 1 == on; 0 == off
        self.setRegisterBit(ADXL345_ACT_INACT_CTL, 2, 1)
        self.setRegisterBit(ADXL345_ACT_INACT_CTL, 1, 1)
        self.setRegisterBit(ADXL345_ACT_INACT_CTL, 0, 1)

        self.setRegisterBit(ADXL345_TAP_AXES, 2, 0)
        self.setRegisterBit(ADXL345_TAP_AXES, 1, 0)
        self.setRegisterBit(ADXL345_TAP_AXES, 0, 0)

        #set values for what is a tap, and what is a double tap (0-255)
        #setTapThreshold(50); # 62.5mg per increment
        self.writeTo(ADXL345_THRESH_TAP, 50)

        self.writeTo(ADXL345_DUR, 15)

        self.writeTo(ADXL345_LATENT, 80)

        #setDoubleTapWindow(200); # 1.25ms per increment
        self.writeTo(ADXL345_WINDOW, 200)

        #set values for what is considered freefall (0-255)

        self.writeTo(ADXL345_THRESH_FF, 7)

        self.writeTo(ADXL345_TIME_FF, 45)
        #setting all interrupts to take place on int pin 1
        #I had issues with int pin 2, was unable to reset it

        self.setRegisterBit(ADXL345_INT_MAP, ADXL345_INT_SINGLE_TAP_BIT,   ADXL345_INT1_PIN)
        self.setRegisterBit(ADXL345_INT_MAP, ADXL345_INT_DOUBLE_TAP_BIT,   ADXL345_INT1_PIN)
        self.setRegisterBit(ADXL345_INT_MAP, ADXL345_INT_FREE_FALL_BIT,    ADXL345_INT1_PIN)
        self.setRegisterBit(ADXL345_INT_MAP, ADXL345_INT_ACTIVITY_BIT,     ADXL345_INT1_PIN)
        self.setRegisterBit(ADXL345_INT_MAP, ADXL345_INT_INACTIVITY_BIT,   ADXL345_INT1_PIN)

        #register interrupt actions - 1 == on; 0 == off
        self.setRegisterBit(ADXL345_INT_ENABLE, ADXL345_INT_SINGLE_TAP_BIT, 1)
        self.setRegisterBit(ADXL345_INT_ENABLE, ADXL345_INT_DOUBLE_TAP_BIT, 1)
        self.setRegisterBit(ADXL345_INT_ENABLE, ADXL345_INT_FREE_FALL_BIT,  1)
        self.setRegisterBit(ADXL345_INT_ENABLE, ADXL345_INT_ACTIVITY_BIT,   1)
        self.setRegisterBit(ADXL345_INT_ENABLE, ADXL345_INT_INACTIVITY_BIT, 1)

    def acc_adxl345_read_xyz(self):
        ADXL345_TO_READ = (6)
        _buff = self.readFrom(ADXL345_DATAX0, ADXL345_TO_READ) #read the acceleration data from the ADXL345
        if _buff[1] <= 0:
            x=_buff[0]
        else:
            x=(_buff[0]-255)

        if _buff[3] <= 0:
            y=_buff[2]
        else:
            y=(_buff[2]-255)

        if _buff[5] <= 0:
            z=_buff[4]
        else:
            z=(_buff[4]-255)

        #x = int(((_buff[1]) << 8) | _buff[0]) 
        #y = int(((_buff[3]) << 8) | _buff[2]) 
        #z = int(((_buff[5]) << 8) | _buff[4]) 

        #print("%d, %d, %d\r\n", x, y, z) 
        return [x,y,z]

    def acc_adxl345_read_acc(self):
        __Gains = [0.00376390, 0.00376009, 0.00389265]
        xyz=self.acc_adxl345_read_xyz()

        ax = xyz[0] * __Gains[0]
        ay = xyz[1] * __Gains[1]
        az = xyz[2] * __Gains[2]
        return [ax,ay,az]

    def get_acc_adxl345_property(self,xyz):
        axyz=self.acc_adxl345_read_acc()
        if(xyz == 0):
            return axyz[0]
        if(xyz == 1):
            return axyz[1]
        if(xyz == 2):
            return axyz[2]

"""
acceleration = AccelerationAdxl345()
acceleration.acc_adxl345_init()
acceleration.get_acc_adxl345_property(0)
acceleration.get_acc_adxl345_property(1)
acceleration.get_acc_adxl345_property(2)
"""