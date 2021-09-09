import sensor, image, time, lcd, video, math
import utime
import random

rows = [x for x in range(300, 0, -10)]

# Display
def lcd_display_string_row(string, row):
    if row < 1 or row > 31:
        return False
    lcd.draw_string(0,(row-1)*10, str(string), lcd.RED, lcd.WHITE)

def lcd_string(string, x, y):
    lcd.draw_string(x,y, str(string), lcd.RED, lcd.WHITE)

def get_img():
    if not global_value.img_global:
        img = image.Image().clear()
        a = img.replace(vflip=True, hmirror=False, transpose=True)
    else:
        img = global_value.img_global
    return img

def load_img(pic_path):
    img = image.Image(pic_path)
    img = img.resize(240,320)
    lcd.display(img)
    del(img)

def draw_circle(x, y, r):
    img = get_img()
    img.draw_circle(x, y, r, color = (255, 0, 0), thickness = 2, fill = False)
    lcd.display(img)
    del(img)

def draw_rectangle_wh(width, heigth, X_center, Y_center):
    img = get_img()
    area = (X_center-(int)(width/2), Y_center-(int)(heigth/2), width, heigth)
    img.draw_rectangle(area, color = (255, 0, 0), thickness = 2, fill = False)
    lcd.display(img)
    del(img)

def draw_rectangle_minmax(Xmin, Ymin, Xmax, Ymax):
    img = get_img()
    area = (Xmin, Ymin, Xmax - Xmin, Ymax - Ymin)
    img.draw_rectangle(area, color = (255, 0, 0), thickness = 2, fill = False)
    lcd.display(img)
    del(img)

def snapshot(picture_name=None):
    img = sensor.snapshot()
    a = img.replace(vflip=True, hmirror=False, transpose=True)
    if picture_name:
        picname = ("/sd/" + str(picture_name) + ".jpg")
        img.save(picname)
    return img

def take_video(second, video_name):
    videoname = ("/sd/" + str(video_name) + ".avi")
    v = video.open(videoname, record=1, interval=200000, quality=50)
    i = 0
    while True:
        img = snapshot()
        lcd.display(img)
        img_len = v.record(img)
        i += 1
        if i >= second*5:
            break
    v.record_finish()
    lcd.clear()

class global_value:
    threshold = 4000
    img_global = 0
    flag_disp_str = 0
    flag_disp_line = 0
    row = 0

def set_sensor_threshold(threshold_value):
    global_value.threshold = threshold_value

def get_sensor_threshold():
    return global_value.threshold

def find_max(a, m=2):
    try:
        list_0 = [a[i].magnitude() for i in range(len(a))]
    except:
        list_0 = [a[i][2]*a[i][3] for i in range(len(a))]
    max_value = max(list_0)
    indent = list_0.index(max_value)

    try:
        x = a[indent].x()*m
        y = a[indent].y()*m
        r = a[indent].r()*m
        a = int(math.pow(r, 2)*math.pi)
        tuple_0 = (x, y, r, a)
    except:
        xmin = a[indent][0]*m
        ymin = a[indent][1]*m
        w = a[indent][2]*m
        h = a[indent][3]*m
        x_cent = (xmin + int(w/2))
        y_cent = (ymin + int(h/2))
        a = w*h
        tuple_0 = (x_cent, y_cent, w, h, a)

    return tuple_0

def compare_lists(real, std):
    result = True
    print(std)
    print(real)
    for i in [0, 2, 4]:
        if (std[i] <= real[i]):
            pass
        else:
            #print("false: i", i)
            result = False

    for q in [1, 3, 5]:
        if (std[q] >= real[q]):
            pass
        else:
            #print("false: q", q)
            result = False

    return result

# random
def define_random(value_one, value_two):
    if type(value_one)==int and type(value_two)==int:
        rand_value = random.randint(int(value_one), int(value_two))
    else:
        rand_value = random.uniform(float(value_one), float(value_two))
    return rand_value

def camera_init():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    # ov2640 id:9794 ,ov5642 id:22082
    if sensor.get_id() == 9794:
        sensor.set_hmirror(1)
        sensor.set_vflip(1)
    else:
        sensor.set_hmirror(0)
        sensor.set_vflip(1)
    lcd.rotation(1)

class Detection:

    def __init__(self):
        self.row = global_value.row
        global_value.row = global_value.row + 1

    def get_detection_result(self):
        pass

    def get_detection_status(self, *args):
        self._tuple = None
        _list = self.get_detection_result(*args)
        if _list:
            return True
        else:
            return False

    def get_detection_property(self, _type, *args):
        self._tuple = None
        _list = self.get_detection_result(*args)
        if not _list:
            return (0)

        if _type == 0:
            return _list
        else:
            return _list[_type-1]

class AprilTagDetection(Detection):

    def get_detection_result(self, tag_id):
        img = snapshot()
        global_value.img_global = img
        img_copy = img.resize(120,160)
        img_copy = img_copy.to_grayscale()

        tag_list = img_copy.find_apriltags(families=image.TAG36H11)

        for t in tag_list:
                img.draw_rectangle((t.x()*2,t.y()*2, t.w()*2, t.h()*2), color = (255, 0, 0), thickness=2)
                img.draw_cross(t.cx()*2, t.cy()*2, color = (0, 255, 0), thickness=2)
                if t.id() != tag_id:
                    tag_list.remove(t)

        if len(tag_list) > 0:
            self._tuple = find_max(tag_list)
            global_value.img_global.draw_string(8, rows[self.row], ("Tag: %d,%d,%d,%d" %(self._tuple[0], self._tuple[1], self._tuple[2], self._tuple[3])), color=(0xff, 0xff, 0xff), scale=1.5, mono_space=False)

        lcd.display(img)
        del(img)
        del(img_copy)
        return self._tuple

class CircleDetection(Detection):

    def get_detection_result(self):
        img = snapshot()
        global_value.img_global = img
        img_copy = img.resize(120,160)
        img_copy = img_copy.to_grayscale()

        circle_list = img_copy.find_circles(x_stride=2, y_stride=1, threshold = global_value.threshold, x_margin = 10, y_margin = 10, r_margin = 10,
                r_min = 2, r_max = 100, r_step = 2)

        for c in circle_list:
            img.draw_circle(c.x()*2, c.y()*2, c.r()*2, color = (0x1c, 0xa2, 0xff), thickness=2)
            img.draw_cross(c.x()*2, c.y()*2, color = (0x1c, 0xa2, 0xff), thickness=2)

        if len(circle_list) > 0:
            self._tuple = find_max(circle_list)
            global_value.img_global.draw_string(8, rows[self.row], ("Circle: %d %d %d" %(self._tuple[0], self._tuple[1], self._tuple[2])), color=(0xff, 0xff, 0xff), scale=1.5, mono_space=False)

        lcd.display(img)
        del(img)
        del(img_copy)
        return self._tuple

class RectangleDetection(Detection):

    def get_detection_result(self):
        img = snapshot()
        global_value.img_global = img
        img_copy = img.resize(120,160)
        img_copy = img_copy.to_grayscale()

        rectangle_list = img_copy.find_rects(threshold = global_value.threshold*6)

        for r in rectangle_list:
            img.draw_rectangle((r.x()*2, r.y()*2, r.w()*2, r.h()*2), color = (0x1c, 0xa2, 0xff), thickness=2)

        if len(rectangle_list) > 0:
            self._tuple = find_max(rectangle_list)
            global_value.img_global.draw_string(8, rows[self.row], ("Rect: %d,%d,%d,%d" % (self._tuple[0], self._tuple[1], self._tuple[2], self._tuple[3])), color=(0xff, 0xff, 0xff), scale=1.5, mono_space=False)

        lcd.display(img)
        del(img)
        del(img_copy)
        return self._tuple

class FaceDetection(Detection):

    def __init__(self):
        global_value.flag_disp_line = 1
        self.row = global_value.row
        global_value.row = global_value.row + 1
        self.face_cascade = image.HaarCascade("frontalface", stages=25)

    def get_detection_result(self):
        img = snapshot()
        global_value.img_global = img
        img_copy = img.resize(120,160)
        img_copy = img_copy.to_grayscale()
        faces_list = img_copy.find_features(self.face_cascade, threshold=0.3, scale_factor=1.25)

        for face in faces_list:
            img.draw_rectangle((face[0]*2, face[1]*2, face[2]*2, face[3]*2), color = (0xff, 0xff, 0xff), thickness=3)

        if len(faces_list) > 0:
            self._tuple = find_max(faces_list)
            global_value.img_global.draw_string(8, rows[self.row], ("Face: %d,%d,%d,%d" % (self._tuple[0], self._tuple[1], self._tuple[2], self._tuple[3])), color=(0xff, 0xff, 0xff), scale=1.5, mono_space=False)

        lcd.display(img)
        del(img)
        del(img_copy)
        return self._tuple

class ColorTracking(object):

    def __init__(self):
        self.r = [(320//2)-(50//2), (240//2)-(50//2), 50, 50] # 50x50 center of QVGA.
        self.threshold = [0]*6 # Middle L, A, B values.
        self.row = global_value.row
        global_value.row = global_value.row + 1

    def initialize_color_tracking(self):
        for i in range(60):
            img = snapshot()
            img.draw_rectangle(self.r)
            lcd.display(img)
        for i in range(60):
            img = snapshot() # Take a picture and return the image.
            hist = img.get_histogram(roi=self.r)
            lo = hist.get_percentile(0.01) # Get the CDF of the histogram at the 1% range (ADJUST AS NECESSARY)!
            hi = hist.get_percentile(0.7) # Get the CDF of the histogram at the 99% range (ADJUST AS NECESSARY)!
            # Average in percentile values.
            self.threshold[0] = (self.threshold[0] + lo.l_value()) // 2
            self.threshold[1] = (self.threshold[1] + hi.l_value()) // 2
            self.threshold[2] = (self.threshold[2] + lo.a_value()) // 2
            self.threshold[3] = (self.threshold[3] + hi.a_value()) // 2
            self.threshold[4] = (self.threshold[4] + lo.b_value()) // 2
            self.threshold[5] = (self.threshold[5] + hi.b_value()) // 2
            for blob in img.find_blobs([self.threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=10):
                img.draw_rectangle(blob.rect())
                img.draw_cross(blob.cx(), blob.cy())
                img.draw_rectangle(self.r)
            lcd.display(img)

    def get_object_property(self, information, argu):
        if information is not None:
            img = snapshot()
            global_value.img_global = img

            object_list = img.find_blobs([information], pixels_threshold=100, area_threshold=100, merge=True, margin=10)
            for blob in object_list:
                img.draw_rectangle(blob.rect(),color = (0xff, 0xff, 0xff), thickness=3)
                img.draw_cross(blob.cx(), blob.cy())

            if len(object_list) > 0:
                object_tuple = find_max(object_list, m=1)
                global_value.img_global.draw_string(8, rows[self.row], ("Object: %d,%d,%d,%d" % (object_tuple[0], object_tuple[1], object_tuple[2], object_tuple[3])), color=(0xff, 0xff, 0xff), scale=1.5, mono_space=False)
                lcd.display(img)
                if argu == 0: # (x_cent, y_cent, w, h)
                    return object_tuple
                else:
                    return object_tuple[argu-1]

        lcd.display(img)
        return (0)

class ColorRecognition:

    def __init__(self):
        self.red = (10, 60, -2, 30, -6, 25)
        self.green = (5, 70, -15, 5, -6, 22)
        self.blue = (10, 35, -6, 12, -23, -11)
        self.yellow = (20, 45, -15, 11, -2, 25)
        self.cyan = (20, 58, -15, 1, -6, 1)
        self.purple = (5, 43, -4, 36, -37, 2)
        self.black = (0, 50, -6, 10, -31, 14)
        self.white = (20, 84, -6, 10, -31, 2)

    def recognize_color(self, detector, recognize_type, argu):

        self.threshold = [0]*6
        self.rgb_value = (0, 0, 0)

        detection = detector.get_detection_property(0)

        if not detection:
            return False

        recognition_type = len(detection)

        if recognition_type == 4: # circle
            area = (detection[0]-detection[2], detection[1]-detection[2], 2*detection[2],  2*detection[2])
        elif recognition_type == 5: # rectangle
            w = detection[2]
            h = detection[3]
            Xmin = detection[0]-int(w/2)
            Ymin = detection[1]-int(h/2)
            area = (Xmin, Ymin, w, h)

        hist = global_value.img_global.get_histogram(bins=32, roi=area)
        stat = hist.get_statistics()
        self.rgb_value = image.lab_to_rgb((stat.l_mean(),stat.a_mean(),stat.b_mean()))
        lo = hist.get_percentile(0.1)
        hi = hist.get_percentile(0.9)
        # Average in percentile values.
        self.threshold[0] = (self.threshold[0] + lo.l_value()) // 2
        self.threshold[1] = (self.threshold[1] + hi.l_value()) // 2
        self.threshold[2] = (self.threshold[2] + lo.a_value()) // 2
        self.threshold[3] = (self.threshold[3] + hi.a_value()) // 2
        self.threshold[4] = (self.threshold[4] + lo.b_value()) // 2
        self.threshold[5] = (self.threshold[5] + hi.b_value()) // 2

        if argu == 1:
            return self.rgb_value[0]
        elif argu == 2:
            return self.rgb_value[1]
        elif argu == 3:
            return self.rgb_value[2]
        elif argu == 4:
            return self.rgb_value

        elif argu == 5: #red
            rgbstatus = compare_lists(self.threshold, self.red)
            return rgbstatus
        elif argu == 6: #green
            rgbstatus = compare_lists(self.threshold, self.green)
            return rgbstatus
        elif argu == 7: #blue
            rgbstatus = compare_lists(self.threshold, self.blue)
            return rgbstatus
        elif argu == 8: #yellow
            rgbstatus = compare_lists(self.threshold, self.yellow)
            return rgbstatus
        elif argu == 9: #cyan
            rgbstatus = compare_lists(self.threshold, self.cyan)
            return rgbstatus
        elif argu == 10: #purple
            rgbstatus = compare_lists(self.threshold, self.purple)
            return rgbstatus
        elif argu == 11: #black
            rgbstatus = compare_lists(self.threshold, self.black)
            return rgbstatus
        elif argu == 12:# white
            rgbstatus = compare_lists(self.threshold, self.white)
            return rgbstatus

# line_following
class Global_GRAYSCALE_THRESHOLD:
    GRAYSCALE_THRESHOLD = [(0, 66)]
    roi_r = 30
    roi_g = 50
    roi_b = 70

def Set_GRAYSCALE_THRESHOLD(line_color):
    if line_color == 1:
        Global_GRAYSCALE_THRESHOLD.GRAYSCALE_THRESHOLD = [(0, 66)]
    elif line_color == 2:
        Global_GRAYSCALE_THRESHOLD.GRAYSCALE_THRESHOLD = [(128, 255)]

def Set_roi_weight(roi_r, roi_g, roi_b):
    Global_GRAYSCALE_THRESHOLD.roi_r = roi_r
    Global_GRAYSCALE_THRESHOLD.roi_g = roi_g
    Global_GRAYSCALE_THRESHOLD.roi_b = roi_b

def track_line():
    r_weight = Global_GRAYSCALE_THRESHOLD.roi_r/100
    g_weight = Global_GRAYSCALE_THRESHOLD.roi_g/100
    b_weight = Global_GRAYSCALE_THRESHOLD.roi_b/100
    global ROIS

    ROIS = [ # [ROI, weight]
            (0, 110, 120, 50, r_weight), # You'll need to tweak the weights for your app
            (0,  55, 120, 55, g_weight), # depending on how your robot is setup.
            (0,   0, 120, 55, b_weight)
           ]

    weight_sum = 0
    centroid_sum = 0
    for r in ROIS: weight_sum += r[4] # r[4] is the roi weight.

    img = snapshot() # Take a picture and return the image.
    img_copy = img.resize(120,160)
    img_copy = img_copy.to_grayscale()

    a = img.draw_rectangle(tuple(2*x for x in ROIS[0][0:4]),color = (255, 0, 0))
    a = img.draw_rectangle(tuple(2*x for x in ROIS[1][0:4]),color = (255, 0, 0))
    a = img.draw_rectangle(tuple(2*x for x in ROIS[2][0:4]),color = (255, 0, 0))
    a = img.draw_string(20, 280, 'A', color=(0xff, 0x00, 0x00), scale=3, mono_space=False)
    a = img.draw_string(20, 150, 'B', color=(0xff, 0x00, 0x00), scale=3, mono_space=False)
    a = img.draw_string(20, 30, 'C', color=(0xff, 0x00, 0x00), scale=3, mono_space=False)

    for r in ROIS:
        blobs = img_copy.find_blobs(Global_GRAYSCALE_THRESHOLD.GRAYSCALE_THRESHOLD, roi=r[0:4], merge=True) # r[0:4] is roi tuple.

        if len(blobs) != 0:
            # Find the blob with the most pixels.
            largest_blob = max(blobs, key=lambda b: b.pixels())
            a = img.draw_cross(largest_blob.cx()*2,largest_blob.cy()*2)
            centroid_sum += largest_blob.cx() * r[4] # r[4] is the roi weight.

    if centroid_sum != 0:
        center_pos = (centroid_sum / weight_sum) # Determine center of line.
        a = img.draw_arrow(120, 300, int(2*center_pos), 20, color = (0, 255, 0), thickness=2)
        deflection_angle = 0
        deflection_angle = -math.atan((2*center_pos-120)/90)

        # Convert angle in radians to degrees.
        deflection_angle = math.degrees(deflection_angle)//1
        a = lcd.display(img)
        return deflection_angle
    else:
        a = lcd.display(img)
        return -1000

camera_init()

"""
#TEST SAMPLES - TO DELETE AFTER TESTING

#circle_detection=CircleDetection()
#rectangle_detection=RectangleDetection()
#face_detection=FaceDetection()
#color_tracking = ColorTracking()
color_recognition = ColorRecognition()
apriltag_detection = AprilTagDetection()
#0 - tuple, then the same for detections
#color_tracking.initialize_color_tracking()

while True:
    load_img('first_boot.jpg')
    #circle_detection.get_detection_status()
    #circle_detection.get_detection_property(0) #maxtuple 0 1 2 3
    #color_recognition.recognize_color(1, 5) #check for red circle

    #rectangle_detection.get_detection_status()
    #rectangle_detection.get_detection_property(0) #maxtuple 0 1 2 3 4
    #print(color_recognition.recognize_color(1, 6)) #check for red circle


    #face_detection.get_detection_status()
    #face_detection.get_detection_property(0) #maxtuple
    #print(apriltag_detection.get_detection_status(1, 0))
    #print(apriltag_detection.get_detection_property(1, 0))
    #color_tracking.get_object_property(color_tracking.threshold, 0) #maxtuple 0 1 2 3 4
    #draw_circle(300, 200, 10)
    #draw_rectangle_wh(100, 50, 160, 120)
    #draw_rectangle_minmax(110, 70, 210, 105)
"""
