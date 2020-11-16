from camera import snapshot, global_value, rows
import image, lcd, time
import KPU as kpu


def find_max(a, m=[1.07,1.42]):

    list_0 = [a[i].w()*a[i].h() for i in range(len(a))]
    max_value = max(list_0)
    indent = list_0.index(max_value)

    xmin = a[indent].x()*m[0]
    ymin = a[indent].y()*m[1]
    w = a[indent].w()*m[0]
    h = a[indent].h()*m[1]
    x_cent = xmin + int(w/2)
    y_cent = ymin + int(h/2)

    return int(x_cent), int(y_cent), int(w*h), a[indent].value(), a[indent].classid()


class ObjectDetection(object):
    def __init__(self, FileName, Classes, Anchor, bool=False):
        self.row = global_value.row
        global_value.row = global_value.row + 1
        self.object_detected = None
        self.percent = 0
        self.file_name = FileName
        self.classes = Classes
        self.anchor = Anchor
        self.x_center = 0
        self.y_center = 0
        if bool:
            self.object_detected_task = kpu.load(self.file_name)
            a= kpu.set_outputs(self.object_detected_task, 0, 7, 7, 5*(5+len(self.classes)))
            a = kpu.init_yolo2(self.object_detected_task, 0.1, 0.3, 5, self.anchor)
        else:
            pass
        
    def detect_objects(self, threshold):
        detected = False
        img = snapshot()
        img_copy = img.resize(224,224)
        a = img_copy.pix_to_ai()
        code = kpu.run_yolo2(self.object_detected_task, img_copy)
        if code:
            for i in code:
                if i.value() >= threshold:
                    detected = True
                    new_x, new_y = int(i.x()*1.07), int(i.y()*1.42)
                    roi = (new_x, new_y, int(i.w()*1.07),int(i.h()*1.42))
                    a=img.draw_rectangle(roi, color = (0x1c, 0xa2, 0xff), thickness=2)
                    percent = i.value()
                    object_detected = self.classes[i.classid()]
                    a = img.draw_string(new_x, new_y-14, ("%s %%: %.2f" % (self.object_detected, self.percent)), color=(255,255,255), scale=1.5, mono_space=False)
            self.x_center, self.y_center, self.area, self.percent, self.object_detected  = find_max(code)
            self.object_detected = self.classes[self.object_detected]
            
        a = lcd.display(img)
        del(img)
        del(img_copy)  
        if detected:
            pass
        else:
            self.object_detected = None
            self.percent = -1

    def get_detection_results(self, percent):
        threshold = percent/100
        self.detect_objects(threshold)
        if self.percent >= threshold:
            return self.object_detected
        else:
            return -1

    def is_object(self, _object, percent):
        threshold = percent/100
        self.detect_objects(threshold)
        if self.object_detected == _object and self.percent >= threshold:
            return True
        else:
            return False

    def get_object_property(self, _object, percent, argu):
        threshold = percent/100
        self.detect_objects(threshold)
        if self.object_detected == _object and self.percent >= threshold:
            if argu == 1:
                return self.x_center
            elif argu == 2:
                return self.y_center
            elif argu == 3:
                return self.area
        else:
            return -1

"""
traffic_classes = ["limit_5","limit_80","no_forward","forward","left","right","u_turn","zebra","stop","yield"]
traffic_anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
traffic_filename = 0x400000

number_classes = ["0","1","2","3","4","5","6","7","8","9"]
number_anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
number_filename = 0x600000

traffic = ObjectDetection(traffic_filename, traffic_classes, traffic_anchor, 1)
#number = ObjectDetection(number_filename, number_classes, number_anchor, 1)
while True:
    #traffic.get_detection_results(10)
    #traffic.is_object('stop', 30)
	print(traffic.get_object_property('stop', 50, 3))

    #number.get_detection_results(50)
    #number.is_object('0',50)
	#number.get_object_property('0',30, 1)
"""
