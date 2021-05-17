from modules import ws2812
from maix_motor import Maix_motor
import time
from camera import *
from object_detection import *
from gpio import *

traffic_classes = ["limit_5","limit_80","no_forward","forward","left","right","u_turn","zebra","stop","yield"]
traffic_anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
traffic_filename = 0x5f5000
traffic = ObjectDetection(traffic_filename, traffic_classes, traffic_anchor, 1)

circle_detection=CircleDetection()
color_recognition = ColorRecognition()

class globalvals:
    state = 0
    i = 0
    result = 0

ws2812_2 = ws2812(3, 5, 2, 3)

def start_handler_0():
    pass
    globalvals.state = 0
    for globalvals.i in range(0, 255, 5):
        time.sleep(0.02)
        ws2812_2.set_led(0,(0, globalvals.i, 0))
        ws2812_2.display()
        ws2812_2.set_led(1,(0, globalvals.i, 0))
        ws2812_2.display()
    for globalvals.i in range(90, 30, -3):
        time.sleep(0.02)
        Maix_motor.servo_angle(2, globalvals.i)
        Maix_motor.servo_angle(1, globalvals.i)
    utime.sleep_ms(200)
    for globalvals.i in range(30, 150, 3):
        time.sleep(0.02)
        Maix_motor.servo_angle(2, globalvals.i)
        Maix_motor.servo_angle(1, globalvals.i)
    utime.sleep_ms(200)
    for globalvals.i in range(150, 90, -3):
        time.sleep(0.02)
        Maix_motor.servo_angle(2, globalvals.i)
        Maix_motor.servo_angle(1, globalvals.i)
    speaker(3, 2, 1/8)
    speaker(3, 9, 1/8)
    speaker(3, 18, 1/8)
    speaker(3, 9, 1/8)
    speaker(3, 18, 1/8)
    while True:
        time.sleep(0.02)
        if globalvals.state == 0:
            Maix_motor.motor_run(0, 0, 0)
            if traffic.is_object("forward", 50):
                globalvals.state = 2
            if color_recognition.recognize_color(circle_detection, 1, 6):
                globalvals.state = 1
        
        if globalvals.state == 1:
            if Line_Finder(5, 1) and Line_Finder(6, 1):
                Maix_motor.motor_motion(1, 1, 0)
            else:
                if Line_Finder(5, 1):
                    Maix_motor.motor_motion(1, 3, 0)
                if Line_Finder(6, 1):
                    Maix_motor.motor_motion(1, 4, 0)
            if color_recognition.recognize_color(circle_detection, 1, 5):
                globalvals.state = 0
        if globalvals.state == 2:
            globalvals.result = traffic.get_detection_results(50)
            if str("left") in str(globalvals.result):
                Maix_motor.motor_motion(1, 4, 0)
            if str("right") in str(globalvals.result):
                Maix_motor.motor_motion(1, 3, 0)
            if str("forward") in str(globalvals.result):
                Maix_motor.motor_motion(1, 1, 0)
            if str("stop") in str(globalvals.result):
                globalvals.state = 0

lcd.display(image.Image('logo.jpg'))
msg = 'Put "Forward" flashcard in front of the camera to start traffic sign detection mode. Put red circle flashcard in front of the camera to start line following mode'
num_rows = len(msg)//28
for i in range(num_rows+3):
	lcd.draw_string(5, i*15, msg[i*28:i*28+28], lcd.RED, lcd.WHITE)
time.sleep(2)
start_handler_0()

