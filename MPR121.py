
from machine import I2C
import time


# MPR121 Register Defines
MHD_R	= 0x2B
NHD_R	= 0x2C
NCL_R 	= 0x2D
FDL_R	= 0x2E
MHD_F	= 0x2F
NHD_F	= 0x30
NCL_F	= 0x31
FDL_F	= 0x32
ELE0_T	= 0x41
ELE0_R	= 0x42
ELE1_T	= 0x43
ELE1_R	= 0x44
ELE2_T	= 0x45
ELE2_R	= 0x46
ELE3_T	= 0x47
ELE3_R	= 0x48
ELE4_T	= 0x49
ELE4_R	= 0x4A
ELE5_T	= 0x4B
ELE5_R	= 0x4C
ELE6_T	= 0x4D
ELE6_R	= 0x4E
ELE7_T	= 0x4F
ELE7_R	= 0x50
ELE8_T	= 0x51
ELE8_R	= 0x52
ELE9_T	= 0x53
ELE9_R	= 0x54
ELE10_T	= 0x55
ELE10_R	= 0x56
ELE11_T	= 0x57
ELE11_R	= 0x58
FIL_CFG	= 0x5D
ELE_CFG	= 0x5E
GPIO_CTRL0	= 0x73
GPIO_CTRL1	= 0x74
GPIO_DATA	= 0x75
GPIO_DIR	= 0x76
GPIO_EN		= 0x77
GPIO_SET	= 0x78
GPIO_CLEAR	= 0x79
GPIO_TOGGLE	= 0x7A
ATO_CFG0	= 0x7B
ATO_CFGU	= 0x7D
ATO_CFGL	= 0x7E
ATO_CFGT	= 0x7F


# Global Constants
TOU_THRESH	= 0x0F
REL_THRESH	= 0x0A

class i2ctouchsensor():
    def __init__(self, addr=0x5A):
        self.i2c_device = I2C(I2C.I2C0, freq=100000, scl=30, sda=31)
        time.sleep(0.1)
        self.initialize()

    def set_register(self, address, r, v):
        #self.i2c_device.writeto_mem(address, r & 0xFF, v & 0xFF, mem_size=8)
        self.i2c_device.writeto(address,bytearray([r & 0xFF, v & 0xFF]))
    def mpr121_setup(self):      
         # Section A - Controls filtering when data is > baseline.  
        self.set_register(0x5A, MHD_R, 0x01)    
        self.set_register(0x5A, NHD_R, 0x01)   
        self.set_register(0x5A, NCL_R, 0x00)   
        self.set_register(0x5A, FDL_R, 0x00)       

        # Section B - Controls filtering when data is < baseline.    
        self.set_register(0x5A, MHD_F, 0x01)    
        self.set_register(0x5A, NHD_F, 0x01)    
        self.set_register(0x5A, NCL_F, 0xFF)    
        self.set_register(0x5A, FDL_F, 0x02)       

        # Section C - Sets touch and release thresholds for each electrode    
        self.set_register(0x5A, ELE0_T, TOU_THRESH)    
        self.set_register(0x5A, ELE0_R, REL_THRESH)       
        self.set_register(0x5A, ELE1_T, TOU_THRESH)    
        self.set_register(0x5A, ELE1_R, REL_THRESH)       
        self.set_register(0x5A, ELE2_T, TOU_THRESH)   
        self.set_register(0x5A, ELE2_R, REL_THRESH)        
        self.set_register(0x5A, ELE3_T, TOU_THRESH)   
        self.set_register(0x5A, ELE3_R, REL_THRESH)      
        self.set_register(0x5A, ELE4_T, TOU_THRESH)    
        self.set_register(0x5A, ELE4_R, REL_THRESH)       
        self.set_register(0x5A, ELE5_T, TOU_THRESH)    
        self.set_register(0x5A, ELE5_R, REL_THRESH)        
        self.set_register(0x5A, ELE6_T, TOU_THRESH)    
        self.set_register(0x5A, ELE6_R, REL_THRESH)       
        self.set_register(0x5A, ELE7_T, TOU_THRESH)   
        self.set_register(0x5A, ELE7_R, REL_THRESH)       
        self.set_register(0x5A, ELE8_T, TOU_THRESH)    
        self.set_register(0x5A, ELE8_R, REL_THRESH)        
        self.set_register(0x5A, ELE9_T, TOU_THRESH)    
        self.set_register(0x5A, ELE9_R, REL_THRESH)       
        self.set_register(0x5A, ELE10_T, TOU_THRESH)   
        self.set_register(0x5A, ELE10_R, REL_THRESH)        
        self.set_register(0x5A, ELE11_T, TOU_THRESH)   
        self.set_register(0x5A, ELE11_R, REL_THRESH)       


        # Section D   
        # Set the Filter Configuration  
        # Set ESI2    
        self.set_register(0x5A, FIL_CFG, 0x04)   
        #self.set_register(0x5A,ATO_CFGU, 0xC9)	# USL = (Vdd-0.7)/vdd*256 = 0xC9 @3.3V   mpr121Write(ATO_CFGL, 0x82)	# LSL = 0.65*USL = 0x82 @3.3V
        #self.set_register(0x5A,ATO_CFGL, 0x82)  # Target = 0.9*USL = 0xB5 @3.3V
        #self.set_register(0x5A,ATO_CFGT,0xb5)
        #self.set_register(0x5A,ATO_CFG0, 0x1B)
        # Section E   
        # Electrode Configuration    
        # Set ELE_CFG to 0x00 to return to standby mode    
        self.set_register(0x5A, ELE_CFG, 0x0C)  # Enables all 12 Electrodes        
        # Section F   
        # Enable Auto Config and auto Reconfig    

    def  initialize(self):
        self.mpr121_setup()

    def getTouchState(self):
        result = 0
        time.sleep(.001)
        bytes=self.i2c_device.readfrom(0x5A, 2)
        result = int(bytes[1]) * 256 + int(bytes[0])
        return result

    
    def getTouchSensorValue(self, channal):
        value = self.getTouchState()
        for i in range(12):
            if (value &(1<<i)):
                return i==channal
            #time.sleep_ms(100)
                
"""
TouchSensor = i2ctouchsensor()

while True:
    if (TouchSensor.getTouchSensorValue(1)):
        print(1)
    time.sleep(.5)
 
"""