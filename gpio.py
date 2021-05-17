from Maix import GPIO
import time, image, lcd
from Maix import FPIOA
from machine import Timer,PWM
from fpioa_manager import fm
from fpioa_manager import *
from modules import ultrasonic
import network
from camera import *

board_info =  {
      'hardware': 
      {
      'BOOT_KEY': 16,
      'LED_R': 13,
      'LED_G': 12,
      'LED_B': 14,
      },
      'interfaces':
      {
      'WIFI_TX': 6,
      'WIFI_RX': 7,
      'WIFI_EN': 8,
      'MIC0_WS': 19,
      'MIC0_DATA': 20,
      'MIC0_BCK': 18,
      'I2S_WS': 33,
      'I2S_DA': 34,
      'I2S_BCK': 35,
      'ESP32_CS': 25,
      'ESP32_RST': 8,
      'ESP32_RDY': 9,
      'ESP32_MOSI': 28,
      'ESP32_MISO': 26,
      'ESP32_SCLK': 27,
      },
      'gpio':
      {
       0:4,
       1:5,
       2: GPIO.GPIOHS21,
       3: GPIO.GPIOHS22,
       4: GPIO.GPIOHS23,
       5: GPIO.GPIOHS24,
       6: GPIO.GPIOHS20,
       7: GPIO.GPIOHS15,
       8: GPIO.GPIOHS14,
       9: GPIO.GPIOHS13,
       10: GPIO.GPIOHS12,
       11: GPIO.GPIOHS11,
       12: GPIO.GPIOHS10,
       13: GPIO.GPIO3,
      }
  }

# gpio
def gpio_init():

    fm.register(21,fm.fpioa.GPIOHS21) # 2
    fm.register(22,fm.fpioa.GPIOHS22)
    fm.register(23,fm.fpioa.GPIOHS23)
    fm.register(24,fm.fpioa.GPIOHS24)
    fm.register(32,fm.fpioa.GPIOHS20) #6
    fm.register(15,fm.fpioa.GPIOHS15)
    fm.register(14,fm.fpioa.GPIOHS14)
    fm.register(13,fm.fpioa.GPIOHS13)
    fm.register(12,fm.fpioa.GPIOHS12)
    fm.register(11,fm.fpioa.GPIOHS11)
    fm.register(10,fm.fpioa.GPIOHS10)
    fm.register(3, fm.fpioa.GPIO3)    # 13

def set_gpio_output(pin_number, status):
    global board_info
    _pin = board_info['gpio'][pin_number]
    _pinObj = GPIO(_pin, GPIO.OUT, GPIO.PULL_NONE)
    _pinObj.value(status)

def get_gpio_input(pin_number):
    global board_info
    _pin = board_info['gpio'][pin_number]
    _pinObj = GPIO(_pin, GPIO.IN, GPIO.PULL_NONE)
    return _pinObj.value()

def MaixAnalogWrite(pin_number, pwm_value):
    value =  pwm_value/255*100
    if pin_number == 3:
        tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
        PWM(tim, freq=1000, duty=value, pin=GPIO.GPIOHS22)
    elif pin_number == 5:
        tim = Timer(Timer.TIMER0, Timer.CHANNEL1, mode=Timer.MODE_PWM)
        PWM(tim, freq=1000, duty=value, pin=GPIO.GPIOHS24)
    elif pin_number == 6:
        tim = Timer(Timer.TIMER0, Timer.CHANNEL2, mode=Timer.MODE_PWM)
        PWM(tim, freq=1000, duty=value, pin=GPIO.GPIOHS20)
    elif pin_number == 9:
        tim = Timer(Timer.TIMER1, Timer.CHANNEL0, mode=Timer.MODE_PWM)
        PWM(tim, freq=1000, duty=value, pin=GPIO.GPIOHS13)
    elif pin_number == 10:
        tim = Timer(Timer.TIMER1, Timer.CHANNEL1, mode=Timer.MODE_PWM)
        PWM(tim, freq=1000, duty=value, pin=GPIO.GPIOHS12)
    elif pin_number == 11:
        tim = Timer(Timer.TIMER1, Timer.CHANNEL2, mode=Timer.MODE_PWM)
        PWM(tim, freq=1000, duty=value, pin=GPIO.GPIOHS11)

def get_system_time_tick(time):
    if time == 1:
        return time.ticks_ms()
    elif time == 2:
        return time.ticks_us()

# Grove one
# button
def DigitalIn_button(pin_number):
    return get_gpio_input(pin_number)

# Line Finder black: 1 white: 0
def Line_Finder(pin_number, argument):
    value = get_gpio_input(pin_number)
    if argument == value:
        return True
    else:
        return False

#speaker
def tone(pin_number, frequency, duration):
    global board_info
    value = 50
    tim = Timer(Timer.TIMER2, Timer.CHANNEL0, mode=Timer.MODE_PWM)
    tim.start()
    _pin = board_info['gpio'][pin_number]
    PWM(tim, freq=frequency, duty=value, pin=_pin)
    time.sleep_ms(duration)
    tim.stop()

# 0 :stop 1-36: piano 37-58 : C3-B5
def speaker(pin, melody, noteDurations):
    if melody == 0:
        tim = Timer(Timer.TIMER2, Timer.CHANNEL0, mode=Timer.MODE_PWM)
        tim.stop()
        noteDuration = int(noteDurations*1000)
        time.sleep_ms(noteDuration)
        return
        
    listmelody = [0,
    131, 147, 165, 175, 196, 220, 247,  #3, 1 - 7
    262, 294, 330, 349, 392, 440, 494,  #4, 8 - 14
    523, 587, 659, 698, 784, 880, 988,  #5, 15 - 21
    
    139, # C#3, 22
    156, # Eb3, 23
    185, # F#3, 24
    208, # G#3, 25
    233, # Bb3, 26
    
    277, # C#4, 27
    311, # Eb4, 28
    370, # F#4, 29
    415, # G#4, 30
    466, # Bb4, 31
    
    555, # C#5, 32
    622, # Eb5, 33
    740, # F#5, 34
    831, # G#5, 35
    932, # Bb5, 36
    
    1047, 1175, 1319, 1397, 1568, 1760, 1976, #6, 37 - 43
    2093, 2349, 2637, 2794, 3136, 3520, 3951, #7, 44 - 50

    1109, # C#6, 52
    1245, # Eb6, 53
    1480, # F#6, 54
    1661, # G#6, 55
    1865, # Bb6, 56
    
    2217, # C#7, 57
    2489, # Eb6, 58
    2960, # F#6, 59
    3322, # G#6, 60
    3729 # Bb6, 61
    ]

    listnoteDurations = noteDurations
    # to calculate the note duration, take one second
    # divided by the note type.
    #e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    noteDuration = int(listnoteDurations*1000)
    lcd.display(image.Image('logo.jpg'))
    lcd.draw_string(5, 15, 'Note is playing', lcd.RED, lcd.WHITE)
    tone(pin, listmelody[melody], noteDuration)
    #pause for the note's duration plus 30 ms
    #utime.sleep_ms(int(noteDuration*0.01))

ultra_pin = {2:fm.fpioa.GPIOHS21, 3:fm.fpioa.GPIOHS22, 4:fm.fpioa.GPIOHS23,
    5:fm.fpioa.GPIOHS24, 6:fm.fpioa.GPIOHS20, 7:fm.fpioa.GPIOHS15,
    8:fm.fpioa.GPIOHS14, 9:fm.fpioa.GPIOHS13, 10:fm.fpioa.GPIOHS12}
#ultrasonic
def get_ultrasonic_distance(pin):
    try:
        global ultra_pin
        _pin = ultra_pin[pin]
        device = ultrasonic(_pin)
        distance = device.measure(unit = ultrasonic.UNIT_CM, timeout = 3000000)
        time.sleep_ms(5)
        if distance > 100:
            distance = 100
            return (distance)
        else:
            return (distance)
    except:
        return 0

#RGB_LED
class RGB_LED:
    def __init__(self, clk, data, number_leds, clk_gpiohs=0, data_gpiohs=1):

        #fm.register(clk, fm.fpioa.GPIOHS0)
        #fm.register(data, fm.fpioa.GPIOHS1)

        self.clk = GPIO(clk, GPIO.OUT)
        self.data = GPIO(data, GPIO.OUT)
        self.clk.value(1)
        self.data.value(0)
        self.status = []
        for i in range(number_leds):
            self.status.append([0,0,0])

    def check_RGB(self, value):
        if not value in range(0,256):
            raise ValueError("value: [0, 255]")

    def check_HSB(self, value):
        if not value in range(0.0,1.0):
            raise ValueError("value: [0, 1]")

    # red, green, blue
    def set_RGB(self, led, r, g, b):
        self.check_RGB(r)
        self.check_RGB(g)
        self.check_RGB(b)

        self.send_byte(0x00)
        self.send_byte(0x00)
        self.send_byte(0x00)
        self.send_byte(0x00)
        for i in range(len(self.status)):
            if i == led:
                self.status[i]=[r, g, b]
            self.send_color(self.status[i][0], self.status[i][1], self.status[i][2])
        self.send_byte(0x00)
        self.send_byte(0x00)
        self.send_byte(0x00)
        self.send_byte(0x00)

    def send_byte(self, data):
        for i in range(8):
            if data & 0x80:
                self.data.value(1)
            else:
                self.data.value(0)
            self.write_clk()
            data <<= 1

    def write_clk(self):
        self.clk.value(0)
        time.sleep_us(20)
        self.clk.value(1)
        time.sleep_us(20)

    def send_color(self, r, g, b):
        prefix = 0xC0
        if (b & 0x80) == 0:
            prefix |= 0x20
        if (b & 0x40) == 0:
            prefix |= 0x10
        if (g & 0x80) == 0:
            prefix |= 0x08
        if (g & 0x40) == 0:
            prefix |= 0x04
        if (r & 0x80) == 0:
            prefix |= 0x02
        if (r & 0x40) == 0:
            prefix |= 0x01
        self.send_byte(prefix)
        self.send_byte(b)
        self.send_byte(g)
        self.send_byte(r)

def set_rgb_led(pin_number, R, G, B):
    led_num  = 1  # LED number
    if pin_number == 2:
        clk_pin  = GPIO.GPIOHS21
        data_pin = GPIO.GPIOHS22
    elif pin_number == 3:
        clk_pin  = GPIO.GPIOHS22
        data_pin = GPIO.GPIOHS23
    elif pin_number == 4:
        clk_pin  = GPIO.GPIOHS23
        data_pin = GPIO.GPIOHS24
    elif pin_number == 5:
        clk_pin  = GPIO.GPIOHS24
        data_pin = GPIO.GPIOHS20
    elif pin_number == 6:
        clk_pin  = GPIO.GPIOHS20
        data_pin = GPIO.GPIOHS15
    elif pin_number == 7:
        clk_pin  = GPIO.GPIOHS15
        data_pin = GPIO.GPIOHS14
    elif pin_number == 8:
        clk_pin  = GPIO.GPIOHS14
        data_pin = GPIO.GPIOHS13
    led = RGB_LED(clk_pin, data_pin, led_num, 0, 1)
    for i in range(led_num):
        if i%2 == 0:
            r = R
            g = G
            b = B
    led.set_RGB(i, r, g, b)

#ADC
class Analog_ADC:
    def __init__(self):
    
        fm.register(25,fm.fpioa.GPIOHS25)#cs
        fm.register(8,fm.fpioa.GPIOHS8)#rst
        fm.register(9,fm.fpioa.GPIOHS9)#rdy
        print("Use hardware SPI for other maixduino")
        fm.register(28,fm.fpioa.SPI1_D0, force=True)#mosi
        fm.register(26,fm.fpioa.SPI1_D1, force=True)#miso
        fm.register(27,fm.fpioa.SPI1_SCLK, force=True)#sclk
        self.nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS25, rst=fm.fpioa.GPIOHS8, rdy=fm.fpioa.GPIOHS9, spi=1)
            
    def analogRead(self, adc_pin):
        try:
            self.adc_value = self.nic.adc()
            return (self.adc_value[adc_pin])
        except:
            return -1
            
    def getAnalogAvg(self, pin):
        sum_adc = 0
        for i in range(10):
            reading = self.analogRead(pin)
            if reading < 0:
                reading = self.analogRead(pin)
            sum_adc = sum_adc + reading
        avg = sum_adc // 10
        return avg


gpio_init()

# Unit tests
if __name__ == "__main__":
    speaker(3, 1, 1)
    speaker(3, 8, 1)
    speaker(3, 15, 1)
    speaker(3, 4, 1)
    speaker(3, 11, 1)
    speaker(3, 18, 1)
    speaker(3, 7, 1)
    speaker(3, 14, 1)
    speaker(3, 21, 1)
