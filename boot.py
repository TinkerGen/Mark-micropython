from chproduct import product_lang
from fpioa_manager import *
import os, lcd, image, time, uio, sys
from Maix import FPIOA, GPIO, utils
import KPU as kpu
import gc

lang = 'en'

gc.threshold(1024*64)
utils.gc_heap_size(1024*768)
kpu.memtest()

def draw_on_image(img_file, string, pos_x, pos_y, size = 1, space = 1):

    chunks, chunk_size = len(string), 28
    msg_lines = [string[i:i+chunk_size]for i in range(0, chunks, chunk_size)]
    img = image.Image(img_file)
    for line in msg_lines:
        a = img.draw_string(pos_x, pos_y, line, scale=size, color=(255,0,0), x_spacing=1, mono_space=space)
        pos_y += 18
    lcd.display(img)
    del(img)

interface_strings = {
    'zh':{
    'Restoring backup. Hold on.': b'正在恢复备份,请不要关机机器！',
    'Restore backup sucessful. Please reboot MARK': b'恢复备份成功,请重新启动机器！',
    "EIO Error - please turn on the power switch and reboot MARK": b'EIO输入输出错误,请打开开关重新启动机器！',
    "First boot": b'初始化中',
    "Scan QR code to access online documentation": b'扫二维码访问柴火创客教育在线文档',
    },

    'en':{
    'Restoring backup. Hold on.': 'Restoring backup. Hold on.',
    'Restore backup sucessful. Please reboot MARK': 'Restore backup sucessful. Please reboot MARK',
    "EIO Error - please turn on the power switch and reboot MARK": "EIO Error - please turn on the power switch and reboot MARK",
    "First boot": "First boot",
    "Scan QR code to access online documentation": "Scan QR code to access online documentation",
    }
}

def restore_backup(filename='camera.py'):
    global lang, interface_strings

    draw_on_image('/flash/backup.jpg', interface_strings[lang]['Restoring backup. Hold on.'], 10, 10, space = (lang == 'zh'))
    os.remove(filename)
    backup_file = open(filename+".bak", 'r')
    backup = backup_file.read()
    backup_file.close()
    f = open(filename, 'w')
    f.write(backup)
    f.close()
    draw_on_image('/flash/backup.jpg', interface_strings[lang]['Restore backup sucessful. Please reboot MARK'], 10, 10, space = (lang == 'zh'))
    sys.exit()

def exception_output(e):
    global lang, interface_strings

    lang = product_lang()

    if lang == 'zh-cn':
        image.font_load(image.UTF8, 16, 16, 0x753000)
        lang = 'zh'

    pic_path = '/flash/error_' + lang + '.jpg'

    string_io = uio.StringIO()
    sys.print_exception(e, string_io)
    s = string_io.getvalue()

    print(s)

    if str(e) == "[Errno 5] EIO" and 'File "maix_motor.py"' in s:
        draw_on_image(pic_path, interface_strings[lang]["EIO Error - please turn on the power switch and reboot MARK"], 10, 10 , space = (lang == 'zh') )
        sys.exit()
    elif str(e) == "[Errno 5] EIO":
        restore_backup(filename='camera.py')

    img = image.Image(pic_path)

    image.font_free()

    a = img.draw_string(5, 5, s, scale=1, color=(255,0,0), x_spacing=1, mono_space=0)
    lcd.display(img)
    del(img)

    time.sleep(2)

try:
    first_boot = "first_boot" in os.listdir("/flash")

    boot_pressed = 0
    fpioa = FPIOA()
    fpioa.set_function(16, FPIOA.GPIO7)
    test_gpio = GPIO(GPIO.GPIO7, GPIO.IN)

    lcd.init()
    lcd.rotation(1)

    if first_boot:
        draw_on_image('/flash/logo.jpg', interface_strings[lang]['First boot'], 70, 220, size = 2, space = 0)
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
                lcd.draw_string(0, 0, str(boot_pressed), lcd.RED, lcd.WHITE)
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
