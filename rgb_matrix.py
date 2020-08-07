from machine import I2C
import time

currentDeviceAddress = 0x65

class GroveTwoRGBLedMatrixClass(object):

    def __init__(self, addr=currentDeviceAddress, drdy=None):
        self.i2c_device = I2C(I2C.I2C0, freq=100000, scl=30, sda=31)
        time.sleep(0.1)
        self.rgbMatrixData = [0xFF]*64

    def read(self, reg_base, reg, buf):
        self.write(reg)
        time.sleep(.001)
        self.i2c_device.readfrom_into(59,buf)

    def write(self, buf=None):
        if buf is not None:
            self.i2c_device.writeto(currentDeviceAddress, buf)
        # i2c_device.writeto(0x58, bytearray([3,100,100,16,39]))


    def displayFrames(self, buffer, duration_time, forever_flag, frames_number):
        data=[0]*72
        #max 5 frames in storage
        if (frames_number > 5):
            frames_number = 5
        elif(frames_number == 0):
            return
        I2C_CMD_DISP_CUSTOM=0x05
        data[0] = I2C_CMD_DISP_CUSTOM
        data[1] = 0x0
        data[2] = 0x0
        data[3] = 0x0
        data[4] = frames_number

        for i in range(frames_number-1,-1,-1):
            data[5] = i
            for j in range(64):
                data[8+j] = buffer[j+i*64]
            if (i == 0):
                #display when everything is finished.
                data[1] = duration_time & 0xff
                data[2] = (duration_time >> 8) & 0xff
                data[3] = forever_flag
            cmd = bytearray(data)
            self.write(cmd)
            time.sleep(.001)

    def rgbMatrixOnPoint(self, x, y, c):
        if(x<0 or x>7 or y<0 or y>7):
            return
        color_value={'red':0x00, 'orange': 0x12, 'yellow':0x18,'green':0x52,'cyan':0x7f,'blue':0xaa,'purple':0xc3,'pink':0xdc,'white':0xfe,'black':0xff}    
        self.rgbMatrixData[x*8+y] = color_value[c]
        self.displayFrames(self.rgbMatrixData,0,1,1)

    def displayString(self, string, duration_time, forever_flag, color):
        data=[0]*36
        lengh = len(string)

        if(lengh >= 28):
            lengh = 28

        for i in range(lengh):
            data[i + 6] = ord(string[i])
        I2C_CMD_DISP_STR = 0x04
        data[0] = I2C_CMD_DISP_STR
        data[1] = forever_flag
        data[2] = duration_time & 0xff
        data[3] = (duration_time >> 8) & 0xff
        data[4] = lengh
        data[5] = color

        if (lengh > 25):
            cmd = bytearray(data[0:(lengh - 25)+31])
            self.write(cmd)
            time.sleep_ms(5)
            #cmd1 = bytearray(data[31:(lengh - 25)+31])
            #self.write(cmd1)
        else:
            cmd2 = bytearray(data[0:(lengh + 6)])
            self.write(cmd2)
            #i2cSendBytes(currentDeviceAddress, data, (lengh + 6))
"""
rgbMatrix=GroveTwoRGBLedMatrixClass()
rgbMatrix.rgbMatrixOnPoint(0,0,'red')    
rgbMatrix.rgbMatrixOnPoint(0,1,'green')   
rgbMatrix.rgbMatrixOnPoint(0,2,'pink') 
#rgbMatrix.displayString('hello',5000,0,1)
rgbMatrixShapeData=[0xff,0xff,0x20,0x20,0x20,0x20,0xff,0xff,
0xff,0x20,0x20,0x20,0x20,0x20,0x20,0xff,0x20,0x20,0x90,0x20,
0x20,0x90,0x20,0x20,0x20,0x20,0x20,0x20,0x20,0x20,0x20,0x20,
0x20,0x20,0x20,0x20,0x20,0x20,0x20,0x20,0x20,0x90,0x20,0x20,
0x20,0x20,0x90,0x20,0xff,0x20,0x90,0x90,0x90,0x90,0x20,0xff,
0xff,0xff,0x20,0x20,0x20,0x20,0xff,0xff
]
rgbMatrix.displayFrames(rgbMatrixShapeData,0,1,1)
"""
