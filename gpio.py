
from Maix import GPIO
import utime, time
from Maix import FPIOA
from machine import Timer,PWM
from fpioa_manager import fm
from fpioa_manager import *
from modules import ultrasonic
import network
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
    """#ADC
    fm.register(25,fm.fpioa.GPIOHS25)#cs
    fm.register(8, fm.fpioa.GPIOHS8)#rst
    fm.register(9, fm.fpioa.GPIOHS9)#rdy
    fm.register(28,fm.fpioa.GPIOHS18)#mosi
    fm.register(26,fm.fpioa.GPIOHS16)#miso
    fm.register(27,fm.fpioa.GPIOHS17)#sclk
    """
gpio = {2:GPIO.GPIOHS21, 3:GPIO.GPIOHS22, 4:GPIO.GPIOHS23, 5:GPIO.GPIOHS24, 6:GPIO.GPIOHS20,
        7:GPIO.GPIOHS15, 8:GPIO.GPIOHS14, 9:GPIO.GPIOHS13, 10:GPIO.GPIOHS12, 11:GPIO.GPIOHS11, 
        12:GPIO.GPIOHS10, 13:GPIO.GPIO3}
 
def set_gpio_output(pin_number, status):
    global gpio
    _pin = gpio[pin_number] 
    _pinObj = GPIO(_pin, GPIO.OUT, GPIO.PULL_NONE)
    _pinObj.value(status)


def get_gpio_input(pin_number):
    global gpio
    _pin = gpio[pin_number]
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
        return utime.ticks_ms()
    elif time == 2:
        return utime.ticks_us()

gpio_init()


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
    value = 50
    tim = Timer(Timer.TIMER2, Timer.CHANNEL0, mode=Timer.MODE_PWM)
    tim.start()
    global gpio
    _pin = gpio[pin_number]
    PWM(tim, freq=frequency, duty=value, pin=_pin)
    utime.sleep_ms(duration)
    tim.stop()

# 0 :stop 1-36: piano 37-58 : C3-B5
def speaker(pin, melody, noteDurations):
    if melody == 0:
        tim = Timer(Timer.TIMER2, Timer.CHANNEL0, mode=Timer.MODE_PWM)
        tim.stop()
        noteDuration = int(noteDurations*1000)
        utime.sleep_ms(noteDuration)
        return
    listmelody = [0, 
              262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494,     #c4-b4
              523, 554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988,     #c5-b5
              1046,1109,1175,1245,1318,1397,1480,1568,1661,1760,1865,1976,    #c6-b6
              131, 147, 165, 175, 196, 220, 247,
              262, 294, 330, 349, 392, 440, 494,
              523, 587, 659, 698, 784, 880, 980, ]
    listnoteDurations = noteDurations
    # to calculate the note duration, take one second
    # divided by the note type.
    #e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    noteDuration = int(listnoteDurations*1000)
    tone(pin, listmelody[melody], noteDuration)
    #pause for the note's duration plus 30 ms
    utime.sleep_ms(30)

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
    def __init__(self, clk, data, number_leds, clk_gpiohs=0, data_gpiohs=1 ):

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
        #ADC
        fm.register(25,fm.fpioa.GPIOHS25)#cs
        fm.register(8, fm.fpioa.GPIOHS8)#rst
        fm.register(9, fm.fpioa.GPIOHS9)#rdy
        fm.register(28,fm.fpioa.GPIOHS18)#mosi
        fm.register(26,fm.fpioa.GPIOHS16)#miso
        fm.register(27,fm.fpioa.GPIOHS17)#sclk
        self.nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS25,rst=fm.fpioa.GPIOHS8,rdy=fm.fpioa.GPIOHS9,
            mosi=fm.fpioa.GPIOHS18,miso=fm.fpioa.GPIOHS16,sclk=fm.fpioa.GPIOHS17)
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
"""
ADC = Analog_ADC()
while True:
    time.sleep(0.5)
    ADC.getAnalogAvg(1)
"""
