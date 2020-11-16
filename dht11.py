
from gpio import *

MAXTIMINGS  = 85

DHT11 = 11
DHT22 = 22
DHT21 = 21
AM2301 = 21

class DHT(object):
    def __init__(self, data_pin,Type=DHT11):
        self.Data_pin = data_pin
        self.datapin = {2:21, 3:22, 4:23, 5:24, 6:GPIO.GPIOHS20, 7:15, 8:14, 9:13, 10:12, 11:11, 12:9, 13:3}
        self.__pinData = GPIO(self.datapin[data_pin], GPIO.OUT)
        self.firstreading = True
        self.__pinData.value(1)
        self._lastreadtime = 0
        self.data=[0]*5
        self.temp = 0
        self.humid = 0

    def read(self):
        i=0
        j=0
        self.__pinData.value(1) 
        #time.sleep(0.25) 

        self.data[0] =  self.data[1] =  self.data[2] =  self.data[3] =  self.data[4] = 0 
        
        # now pull it low for ~20 milliseconds
        pinData = GPIO(self.datapin[self.Data_pin], GPIO.OUT, GPIO.PULL_NONE)
        pinData.value(0) 
        time.sleep_ms(20)
        pinData.value(1)
        time.sleep_us(41)

        DHT11_TIMEOUT = -1
        time_cnt=0
        while(0 == GPIO(self.datapin[self.Data_pin], GPIO.IN).value()):
            time.sleep_us(5)  
            time_cnt = time_cnt+1
            if(time_cnt > 16): 
                return
        
        #DHT11将总线拉高至少80us，为发送传感器数据做准备。
        time_cnt=0
        while(1 == GPIO(self.datapin[self.Data_pin], GPIO.IN).value()):
            time.sleep_us(5)   
            time_cnt = time_cnt+1
            if(time_cnt > 16): 
                return  
        
        
        for j in range(5):
            i = 0
            result=0
            PINC = 1
            for i in range(8):

                while(not (PINC & GPIO(self.datapin[self.Data_pin], GPIO.IN).value())):  # wait for 50us
                    pass
                    #print('wait 50us')
                time.sleep_us(30)

                if(PINC & GPIO(self.datapin[self.Data_pin], GPIO.IN).value()):
                    result |=(1<<(7-i))
                while(PINC & GPIO(self.datapin[self.Data_pin], GPIO.IN).value()):  # wait '1' finish
                    pass
                    #print('wait 1')
            self.data[j] = result

        pinData = GPIO(self.datapin[self.Data_pin], GPIO.OUT, GPIO.PULL_NONE)
        pinData.value(1)   

        dht11_check_sum = (self.data[0]+self.data[1]+self.data[2]+self.data[3]&0xff)
        # check check_sum
        if(self.data[4] is not dht11_check_sum):
            print("DHT11 checksum error")
        #print(self.data) 
        if ((j >= 4) and ( self.data[4] == dht11_check_sum)):
            return True 
        
        return False
        
    def readHumidity(self):
        if (self.read()):
            self.humid = float(self.data[0])
            self.humid = self.humid + float(self.data[1]/10)
        return self.humid

    def readTemperature(self):
        if (self.read()):
            self.temp = float(self.data[2])
            self.temp = self.temp + float(self.data[3]/10)
        return self.temp
"""            
dht = DHT(6)
for i in range(1000):
    #dht.read()
    dht.readHumidity()
    dht.readTemperature()
"""
