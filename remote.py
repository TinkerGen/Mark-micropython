import network, socket, time, utime, sensor, image, lcd, os
from machine import UART
from Maix import GPIO
from maix_motor import Maix_motor
from fpioa_manager import fm, board_info
import ujson

########## config ################
WIFI_SSID = 0
WIFI_PASSWD = 0
server_ip      = 0
server_port    = 3456
pan_angle = 90
tilt_angle = 90
bullet = 90
##################################

# IO map for ESP32 on Maixduino
fm.register(25,fm.fpioa.GPIOHS10)#cs
fm.register(8,fm.fpioa.GPIOHS11)#rst
fm.register(9,fm.fpioa.GPIOHS12)#rdy
fm.register(28,fm.fpioa.GPIOHS13)#mosi
fm.register(26,fm.fpioa.GPIOHS14)#miso
fm.register(27,fm.fpioa.GPIOHS15)#sclk

clock = time.clock()
lcd.init()
lcd.rotation(1)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_vflip(2)

lcd.display(image.Image('remote.jpg'))
time.sleep(1)

nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS10,rst=fm.fpioa.GPIOHS11,rdy=fm.fpioa.GPIOHS12, mosi=fm.fpioa.GPIOHS13,miso=fm.fpioa.GPIOHS14,sclk=fm.fpioa.GPIOHS15)
print("ESP32_SPI firmware version:", nic.version())


while not WIFI_SSID:
    img = sensor.snapshot()
    a = img.replace(vflip=True, hmirror=False, transpose=True)
    res = img.find_qrcodes()
    fps =clock.fps()
    if len(res) > 0:
        a= img.draw_string(2,2, res[0].payload(), color=(0,255,0), scale=1)
        payload = res[0].payload()
        print(payload)
        payloadJSON = ujson.loads(payload)
        WIFI_SSID = payloadJSON["ssid"]
        WIFI_PASSWORD = payloadJSON["password"]
        server_ip = payloadJSON["host"]
        server_port = payloadJSON["port"]
        print(WIFI_SSID, WIFI_PASSWORD, server_ip)
    lcd.display(img)

addr = (server_ip, server_port)
err = 0

while 1:
    try:
        nic.connect(WIFI_SSID, WIFI_PASSWORD)
    except Exception as e:
        err += 1
        print(e)
        if err > 3:
            raise Exception("Conenct AP fail")
        continue
    break
print(nic.ifconfig())
print(nic.isconnected())

def control_motors(data):
    global pan_angle
    global tilt_angle
    global bullet
    if data == b'\x01':
        Maix_motor.motor_motion(2, 1, 0)
    if data == b'\x02':
        Maix_motor.motor_motion(1, 3, 0)
    if data == b'\x03':
        Maix_motor.motor_motion(1, 4, 0)
    if data == b'\x04':
        Maix_motor.motor_motion(2, 2, 0)
    if data == b'\x05':
        Maix_motor.motor_run(0, 0, 0)
        bullet = 90
    if data == b'\x08':
        pan_angle = pan_angle + 2
    if data == b'\x09':
        pan_angle = pan_angle - 2
    if data == b'\x07':
        tilt_angle = tilt_angle + 2
    if data == b'\x06':
        tilt_angle = tilt_angle - 2
    if data == b'\x0b':
        bullet = 40


    if pan_angle > 180: pan_angle = 180
    if pan_angle < 1: pan_angle = 0
    if tilt_angle > 180: tilt_angle = 180
    if tilt_angle < 1: tilt_angle = 0
    Maix_motor.servo_angle(1, pan_angle)
    Maix_motor.servo_angle(2, tilt_angle)
    Maix_motor.servo_angle(3, bullet)


def send_buffer(sock, data, buf_size):
    block = int(len(img_bytes)/buf_size)
    send_len = 0
    for i in range(block):
        send_len = sock.send(img_bytes[i*buf_size:(i+1)*buf_size])
        send_len += send_len
    send_len += sock.send(img_bytes[block*buf_size:])
    return send_len


while True:

# send pic
    sock = socket.socket()
    print(sock)
    try:
        sock.connect(addr)
    except Exception as e:
        print("connect error:", e)
        sock.close()
        continue
    sock.settimeout(0.1)

    count = 0
    err   = 0
    while True:
        clock.tick()

        if err >=10:
            print("socket broken")
            break
        img = sensor.snapshot()
        a = img.replace(vflip=True, hmirror=False, transpose=True)
        img.draw_cross(120, 160)
        lcd.display(img)
        img = img.compress(quality=30)
        img_bytes = img.to_bytes()
        try:
            send_len = send_buffer(sock, img_bytes, 2048)
            data = sock.recv(1)
            print(data)
            control_motors(data)
            if send_len == 0:
                lcd.draw_string(lcd.width()//2-68,lcd.height()//2-4, "send fail", lcd.WHITE, lcd.RED)
                raise Exception("send fail")
        except OSError as e:
            if e.args[0] == 128:
                lcd.draw_string(lcd.width()//2-68,lcd.height()//2-4, "connection closed", lcd.WHITE, lcd.RED)
                break
        except Exception as e:
            print("send fail:", e)
            lcd.draw_string(lcd.width()//2-68,lcd.height()//2-4, "exception", lcd.WHITE, lcd.RED)
            time.sleep(0.1)
            err += 1
            continue
        count += 1
        print("send:", count)
    print("close now")
    sock.close()

