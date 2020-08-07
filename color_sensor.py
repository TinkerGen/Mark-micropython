
from machine import I2C
import time

TCS34725_ADDRESS =(0x29)

TCS34725_COMMAND_BIT=(0x80)

TCS34725_ENABLE=(0x00)
TCS34725_ENABLE_AIEN=(0x10) # RGBC Interrupt Enable 
TCS34725_ENABLE_WEN=(0x08)  # Wait enable - Writing 1 activates the wait timer 
TCS34725_ENABLE_AEN=(0x02)  # RGBC Enable - Writing 1 actives the ADC, 0 disables it 
TCS34725_ENABLE_PON=(0x01)  # Power on - Writing 1 activates the internal oscillator, 0 disables it 
TCS34725_ATIME=(0x01)       # Integration time 
TCS34725_WTIME=(0x03)       # Wait time=(if TCS34725_ENABLE_WEN is asserted) 
TCS34725_WTIME_2_4MS=(0xFF) # WLONG0 = 2.4ms   WLONG1 = 0.029s 
TCS34725_WTIME_204MS=(0xAB) # WLONG0 = 204ms   WLONG1 = 2.45s  
TCS34725_WTIME_614MS=(0x00) # WLONG0 = 614ms   WLONG1 = 7.4s   
TCS34725_AILTL=(0x04)       # Clear channel lower interrupt threshold 
TCS34725_AILTH=(0x05)
TCS34725_AIHTL=(0x06) # Clear channel upper interrupt threshold 
TCS34725_AIHTH=(0x07)
TCS34725_PERS=(0x0C)            # Persistence register - basic SW filtering mechanism for interrupts 
TCS34725_PERS_NONE=(0b0000)     # Every RGBC cycle generates an interrupt                                
TCS34725_PERS_1_CYCLE=(0b0001)  # 1 clean channel value outside threshold range generates an interrupt   
TCS34725_PERS_2_CYCLE=(0b0010)  # 2 clean channel values outside threshold range generates an interrupt  
TCS34725_PERS_3_CYCLE=(0b0011)  # 3 clean channel values outside threshold range generates an interrupt  
TCS34725_PERS_5_CYCLE=(0b0100)  # 5 clean channel values outside threshold range generates an interrupt  
TCS34725_PERS_10_CYCLE=(0b0101) # 10 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_15_CYCLE=(0b0110) # 15 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_20_CYCLE=(0b0111) # 20 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_25_CYCLE=(0b1000) # 25 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_30_CYCLE=(0b1001) # 30 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_35_CYCLE=(0b1010) # 35 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_40_CYCLE=(0b1011) # 40 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_45_CYCLE=(0b1100) # 45 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_50_CYCLE=(0b1101) # 50 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_55_CYCLE=(0b1110) # 55 clean channel values outside threshold range generates an interrupt 
TCS34725_PERS_60_CYCLE=(0b1111) # 60 clean channel values outside threshold range generates an interrupt 
TCS34725_CONFIG=(0x0D)
TCS34725_CONFIG_WLONG=(0x02) # Choose between short and long (12x) wait times via TCS34725_WTIME 
TCS34725_CONTROL=(0x0F)      # Set the gain level for the sensor 
TCS34725_ID=(0x12)           # 0x44 = TCS34721/TCS34725, 0x4D = TCS34723/TCS34727 
TCS34725_STATUS=(0x13)
TCS34725_STATUS_AINT=(0x10)   # RGBC Clean channel interrupt 
TCS34725_STATUS_AVALID=(0x01) # Indicates that the RGBC channels have completed an integration cycle 
TCS34725_CDATAL=(0x14)        # Clear channel data 
TCS34725_CDATAH=(0x15)
TCS34725_RDATAL=(0x16) # Red channel data 
TCS34725_RDATAH=(0x17)
TCS34725_GDATAL=(0x18) # Green channel data 
TCS34725_GDATAH=(0x19)
TCS34725_BDATAL=(0x1A) # Blue channel data 
TCS34725_BDATAH=(0x1B)

CC_COLOR_RED =1
CC_COLOR_GREEN =2
CC_COLOR_BLUE =3
CC_COLOR_BLACK =4
CC_COLOR_OTHER =5
CC_COLOR_WHITE =6

TCS34725_INTEGRATIONTIME_2_4MS = 0xFF #<  2.4ms - 1 cycle    - Max Count: 1024  */
TCS34725_INTEGRATIONTIME_24MS = 0xF6  #**<  24ms  - 10 cycles  - Max Count: 10240 */
TCS34725_INTEGRATIONTIME_50MS = 0xEB  #**<  50ms  - 20 cycles  - Max Count: 20480 */
TCS34725_INTEGRATIONTIME_101MS = 0xD5 #*<  101ms - 42 cycles  - Max Count: 43008 */
TCS34725_INTEGRATIONTIME_154MS = 0xC0 #**<  154ms - 64 cycles  - Max Count: 65535 */
TCS34725_INTEGRATIONTIME_700MS = 0x00  #**<  700ms - 256 cycles - Max Count: 65535 */

TCS34725_GAIN_1X = 0x00  #**<  No gain  */
TCS34725_GAIN_4X = 0x01  #**<  4x gain  */
TCS34725_GAIN_16X = 0x02 #*<  16x gain */
TCS34725_GAIN_60X = 0x03 #*<  60x gain */

class ColorSensor(object):

    def __init__(self, addr=TCS34725_ADDRESS, it=TCS34725_INTEGRATIONTIME_2_4MS, gain=TCS34725_GAIN_1X):
        self.i2c_device = I2C(I2C.I2C0, freq=100000, scl=30, sda=31)
        time.sleep(0.1)
        self._tcs34725Initialised = False
        self._tcs34725IntegrationTime = it
        self._tcs34725Gain = gain

    def read(self, reg_base, reg, buf):
        self.write(reg)
        time.sleep(.001)
        self.i2c_device.readfrom_into(59,buf)

    def write(self, buf=None):
        if buf is not None:
            self.i2c_device.writeto(TCS34725_ADDRESS, buf)

    def write8(self,reg,value):
        if value is not None:
            self.i2c_device.writeto_mem(TCS34725_ADDRESS, TCS34725_COMMAND_BIT | reg, value & 0xFF, mem_size=8)
          
    def read8(self, reg):
        dta_send = bytearray([TCS34725_COMMAND_BIT | reg])
        self.write(dta_send)
        time.sleep(.001)
        num = 1
        bytes=self.i2c_device.readfrom(TCS34725_ADDRESS, num)
        for _b in bytes:
            value = int(_b)
        return value

    def read16(self, reg):
        dta_send = bytearray([TCS34725_COMMAND_BIT | reg])
        self.write(dta_send)
        time.sleep(.001)
        num = 1
        bytes=self.i2c_device.readfrom(TCS34725_ADDRESS, num)
        for _b in bytes:
            t = int(_b)
        bytes=self.i2c_device.readfrom(TCS34725_ADDRESS, num)
        for _b in bytes:
            x = int(_b)
        x <<= 8
        x |= t
        return x

    def enable(self):    
        self.write8(TCS34725_ENABLE, TCS34725_ENABLE_PON)
        time.sleep_ms(3)
        self.write8(TCS34725_ENABLE, TCS34725_ENABLE_PON | TCS34725_ENABLE_AEN)

    def disable(self):
        reg = 0
        reg = self.read8(TCS34725_ENABLE)
        self.write8(TCS34725_ENABLE, reg & ~(TCS34725_ENABLE_PON | TCS34725_ENABLE_AEN))
    
    def begin(self):
        x = self.read8(TCS34725_ID)
        if ((x is not 0x44) and (x is not 0x10)):
            return False
        self._tcs34725Initialised = True
        self.setIntegrationTime(self._tcs34725IntegrationTime)
        self.setGain(self._tcs34725Gain)
        self.enable()
        return True
                
    def setIntegrationTime(self,it):
        if (not self._tcs34725Initialised):
            self.begin()
        self.write8(TCS34725_ATIME, it)
        self._tcs34725IntegrationTime = it
    
    def setGain(self, gain):
        if (not self._tcs34725Initialised):
            self.begin()
        self.write8(TCS34725_CONTROL, gain)
        self._tcs34725Gain = gain
    
    def getRawData(self):
        
        if (not self._tcs34725Initialised):
            self.begin()

        c = self.read16(TCS34725_CDATAL)
        r = self.read16(TCS34725_RDATAL)
        g = self.read16(TCS34725_GDATAL)
        b = self.read16(TCS34725_BDATAL)

        if (self._tcs34725IntegrationTime == TCS34725_INTEGRATIONTIME_2_4MS):
            time.sleep_ms(3)

        elif (self._tcs34725IntegrationTime == TCS34725_INTEGRATIONTIME_24MS):
            time.sleep_ms(24)
            
        elif (self._tcs34725IntegrationTime == TCS34725_INTEGRATIONTIME_50MS):
            time.sleep_ms(50)
            
        elif (self._tcs34725IntegrationTime == TCS34725_INTEGRATIONTIME_101MS):
            time.sleep_ms(101)
            
        elif (self._tcs34725IntegrationTime == TCS34725_INTEGRATIONTIME_154MS):
            time.sleep_ms(154)
            
        elif (self._tcs34725IntegrationTime == TCS34725_INTEGRATIONTIME_700MS):
            time.sleep_ms(700)
            
        return [c,r,g,b]
  
    def setInterrupt(self,i):
        r = self.read8(TCS34725_ENABLE)
        if (i):
            r |= TCS34725_ENABLE_AIEN
        else:
            r &= ~TCS34725_ENABLE_AIEN
        
        self.write8(TCS34725_ENABLE, r)
        
    def get_color_status(self,colorId):
        self.setInterrupt(False)
        time.sleep_ms(100)
        color_list = self.getRawData()
        clearCode = color_list[0]
        redCode = color_list[1]
        greenCode = color_list[2]
        blueCode = color_list[3]
        self.setInterrupt(True)
        if (clearCode > 18000):
            #print("white")
            return colorId == CC_COLOR_WHITE
        
        elif ((clearCode < 2500) and (redCode < (clearCode / 3)) and (greenCode < (clearCode / 2)) and (blueCode < (clearCode / 3))):
            #print("black")
            return colorId == CC_COLOR_BLACK
        elif (redCode > (clearCode / 3))  and  (redCode > greenCode * 2) and (redCode > blueCode * 3):
            #print('red')
            return colorId == CC_COLOR_RED       
        elif (greenCode > (clearCode / 3))  and  (greenCode > redCode * 1) and (greenCode > blueCode * 1):
            #print("green")
            return colorId == CC_COLOR_GREEN

        elif (blueCode > (clearCode / 3))  and  (blueCode > redCode * 1) and ( blueCode > greenCode  * 1):
            #print("blue")
            return colorId == CC_COLOR_BLUE
        else:
            #print("other")
            return colorId == CC_COLOR_OTHER
"""     
color = ColorSensor()

color.begin()
while True:
    color.get_color_status(CC_COLOR_BLACK)
"""

