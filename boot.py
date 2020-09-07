from fpioa_manager import *
import os, Maix, lcd, image, time
from Maix import FPIOA, GPIO
import gc
gc.threshold(65536)

def exception_output(e):
    lcd.clear()
    if str(e) == "[Errno 5] EIO":
        e = "EIO Error - please turn on the power switch and reboot MARK"
    print(e)
    num_rows = len(str(e))//30+1
    for i in range(num_rows):
    	lcd.draw_string(0,i*15, str(e)[i*30:i*30+30], lcd.RED, lcd.BLACK)
    time.sleep(10)

try:
    first_boot = "first_boot" in os.listdir("/flash")

    boot_pressed = 0
    test_pin=16
    fpioa = FPIOA()
    fpioa.set_function(test_pin,FPIOA.GPIO7)
    test_gpio=GPIO(GPIO.GPIO7,GPIO.IN)

    lcd.init()
    lcd.rotation(1)

    if first_boot:
        lcd.display(image.Image('first_boot.jpg'))
        os.remove("/flash/first_boot")
        time.sleep(2)
        gc.collect()
        from preloaded import *

    else:
        lcd.display(image.Image('logo.jpg'))
        start_time =  time.ticks_ms()
        while (time.ticks_ms() - start_time) < 500:
            if test_gpio.value() == 0:
                boot_pressed += 1
                time.sleep(0.5)
                start_time =  time.ticks_ms()
                lcd.draw_string(0, 0, str(boot_pressed), lcd.RED, lcd.BLACK)
        if boot_pressed == 2:
            gc.collect()
            from preloaded import *
        if boot_pressed > 2:
            from remote import *
    gc.collect()
    from user import *

except Exception as e:
    exception_output(e)
    raise
