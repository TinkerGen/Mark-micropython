from gpio import *


"""ChainableLed"""

import array
class ChainableLed(object):
    def __init__(self,clk_pin, data_pin, number_of_leds):
        self.clkpin  = {4:23, 6:GPIO.GPIOHS20, 8:14, 10:12}
        self.datapin = {2:21, 5:24, 7:15, 9:13}
        self.Clk = GPIO(self.clkpin[clk_pin], GPIO.OUT,GPIO.PULL_NONE)
        self.Data = GPIO(self.datapin[data_pin], GPIO.OUT,GPIO.PULL_NONE)
        self._led_state = array.array('B',[0]*3*number_of_leds)
        self.led_num = number_of_leds

    def SendByte(self, b_value):
        for i in range(0,8):
            if ((b_value & 0x80) != 0):
                self.Data.value(1)
            else:
                self.Data.value(0)
            b_value <<= 1
            self.Clk.value(0)
            time.sleep_us(1)
            self.Clk.value(1)
            time.sleep_us(1)

    def SendColor(self, red, green, blue):
        self.prefit = 0xc0
        if ((blue & 0x80) == 0):
            self.prefit |= 0x20
        if ((blue & 0x40) == 0):
            self.prefit |= 0x10
        if ((green & 0x80) == 0):
            self.prefit |= 0x08
        if ((green & 0x40) == 0):
            self.prefit |= 0x04
        if ((red & 0x80) == 0):
            self.prefit |= 0x02
        if ((red & 0x40) == 0):
            self.prefit |= 0x01
        self.SendByte(self.prefit)
        self.SendByte(blue)
        self.SendByte(green)
        self.SendByte(red)

    def setColorRGB(self, led, red, green, blue):
        self.SendByte(0x00)
        self.SendByte(0x00)
        self.SendByte(0x00)
        self.SendByte(0x00)
        _CL_RED = 0
        _CL_GREEN = 1
        _CL_BLUE = 2
        for i in range(0,self.led_num):
            if (i == (led-1)):
                 self._led_state[i*3 + _CL_RED] = red
                 self._led_state[i*3 + _CL_GREEN] = green
                 self._led_state[i*3 + _CL_BLUE] = blue
            self.SendColor(self._led_state[i*3 + _CL_RED], 
                     self._led_state[i*3 + _CL_GREEN], 
                     self._led_state[i*3 + _CL_BLUE])

        self.SendByte(0x00)
        self.SendByte(0x00)
        self.SendByte(0x00)
        self.SendByte(0x00)
        
"""
gpio_init()    
led1 = ChainableLed(6,5,2)  
led2 = ChainableLed(10,9,2) 
while 1:
     led1.setColorRGB(0,50,22,0)
     led1.setColorRGB(1,255,0,0)
     time.sleep(1)
     led1.setColorRGB(0,0,255,0)
     led1.setColorRGB(1,255,255,255)
     time.sleep(1)
     led2.setColorRGB(0,50,22,0)
     led2.setColorRGB(1,255,0,0)
     time.sleep(1)
     led2.setColorRGB(0,0,255,0)
     led2.setColorRGB(1,255,255,255)
     time.sleep(1)
"""


"""next"""
class TM1637(object):
    def __init__(self,clk_pin, data_pin):
        self.clkpin  = {4:23, 6:GPIO.GPIOHS20, 8:14, 10:12}
        self.datapin = {2:21, 5:24, 7:15, 9:13}
        self.Clk = GPIO(self.clkpin[clk_pin], GPIO.OUT, GPIO.PULL_NONE)
        self.Data = GPIO(self.datapin[data_pin], GPIO.OUT, GPIO.PULL_NONE)
        self.Data_pin = self.datapin[data_pin]
        self.TubeTab = [0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f,0x77,0x7c,0x39,0x5e,0x79,0x71]#0~9,A,b,C,d,E,F
        self._PointFlag = 0
        self.Cmd_DispCtrl = 0x0
        self.Cmd_SetData = 0x0
        self.Cmd_SetAddr = 0x0
        self.BRIGHT_TYPICAL = 2
        self.clearDisplay()
        self.set(self.BRIGHT_TYPICAL)

    def start(self):
        self.Clk.value(1)
        self.Data.value(1)
        self.Data.value(0)
        self.Clk.value(0)

    def stop(self):
        self.Clk.value(0)
        self.Data.value(0)
        self.Clk.value(1)
        self.Data.value(1)

    def writeByte(self,wr_data):
        for i in range(8):
            self.Clk.value(0)
            if(wr_data & 0x01):
                self.Data.value(1)
            else:
                self.Data.value(0)
            wr_data >>= 1
            self.Clk.value(1)
        self.Clk.value(0)
        self.Data.value(1)
        self.Clk.value(1)
        Datpin = GPIO(self.Data_pin,GPIO.IN)
        time.sleep_us(50)
        ack = Datpin.value()
        if (ack == 0):
            GPIO(self.Data_pin,GPIO.OUT)
            self.Data.value(0)
        time.sleep_us(50)
        GPIO(self.Data_pin,GPIO.OUT)
        time.sleep_us(50)
        return ack

    def point(self, PointFlag):
        _PointFlag = PointFlag

    def coding(self, DispData):   
        self.POINT_ON = 1
        if (self._PointFlag == self.POINT_ON):
            PointData = 0x80
        else:
            PointData = 0
        if (DispData == 0x7f):
            DispData = 0x00 + PointData
        else: 
            DispData = self.TubeTab[DispData] + PointData
        return DispData

    def display(self, BitAddr, DispData):
        ADDR_FIXED = 0x44
        SegData = self.coding(DispData)
        self.start()       
        self.writeByte(ADDR_FIXED)
        self.stop()
        self.start()
        self.writeByte(BitAddr|0xc0)
        self.writeByte(SegData)
        self.stop()
        self.start()
        self.writeByte(self.Cmd_DispCtrl)
        self.stop()

    def set(self, brightness, SetData=0x40, SetAddr=0xc0):
        self.Cmd_SetData = SetData
        self.Cmd_SetAddr = SetAddr
        self.Cmd_DispCtrl = 0x88 + brightness # Set the brightness and it takes effect the next time it displays.

    def clearDisplay(self):
        self.display(0x00,0x7f)
        self.display(0x01,0x7f)
        self.display(0x02,0x7f)
        self.display(0x03,0x7f)
    
    def showNumber(self,num):
        self.display(3,num%10)
        num = num // 10
        self.display(2,num%10)
        num = num // 10
        self.display(1,num%10)
        num = num // 10
        self.display(0,num%10)
"""        
gpio_init()   
shumaguan = TM1637(4,2)
shumaguan.showNumber(0)
"""

#gpio_init() 
class Grove_LED_Bar(object):
    def __init__(self, data_pin, clk_pin,greenToRed):
        self.datapin = {4:23, 6:GPIO.GPIOHS20, 8:14, 10:12}
        self.clkpin = {2:21, 5:24, 7:15, 9:13}
        self.__pinData = GPIO(self.datapin[data_pin], GPIO.OUT, GPIO.PULL_NONE)
        self.__pinClock = GPIO(self.clkpin[clk_pin], GPIO.OUT, GPIO.PULL_NONE)
        self.__greenToRed = greenToRed
        self.__state = [0x00]*10

    def latchData(self):
        self.__pinData.value(0)
        time.sleep_ms(10)
        for i in range(0,4):
            self.__pinData.value(1)
            self.__pinData.value(0)

    def sendData(self,data):
        state = 0
        for i in range(0,16):
            if (data & 0x8000):
                state1=1
            else:
                state1=0
            self.__pinData.value(state1)
            state = 1-state
            self.__pinClock.value(state)
            data <<= 1
    def setLed(self, led, brightness):
        led = max(1, min(10, led))
        brightness = max(0.0, min(brightness, 1.0))
        led=led-1
        self.__state[led] = ~(~0 << (brightness*8))
        self.setData(self.__state)

    def setData(self,__state):
        GLB_CMDMODE =0x00
        self.sendData(GLB_CMDMODE)
        for i in range(0,10):
            if (self.__greenToRed):
                self.sendData(__state[10-i-1])
            else:
                self.sendData(__state[i])
        self.sendData(0x00)
        self.sendData(0x00)
        self.latchData()
"""
groveLedBar = Grove_LED_Bar(6,5,0)
groveLedBar.setLed(1,1)
groveLedBar.setLed(2,1)
"""
