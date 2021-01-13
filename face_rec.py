from camera import snapshot
import image, lcd, time
import KPU as kpu
import ujson, ubinascii

def _hexlify(data):
    return ubinascii.hexlify(data)

def _unhexlify(data):
    return ubinascii.unhexlify(data)

def _find_max(a, m=[1.07,1.42]):

    list_0 = [a[i].w()*a[i].h() for i in range(len(a))]
    max_value = max(list_0)
    indent = list_0.index(max_value)

    xmin = a[indent].x()*m[0]
    ymin = a[indent].y()*m[1]
    w = a[indent].w()*m[0]
    h = a[indent].h()*m[1]
    x_cent = xmin + int(w/2)
    y_cent = ymin + int(h/2)

    return int(x_cent), int(y_cent), int(w*h), a[indent].value(), (int(xmin), int(ymin), int(w), int(h))

def _write_db(db, id, name, vector):

    if not db:
        print("db is empty")
        db = {}

    vector = _hexlify(vector)

    entry = {"name": name, "vector": vector}
    db[id] = entry

    f = open('/flash/database.db','w')
    entry = ujson.dumps(db)
    f.write(entry)
    f.close()

    return db

def _read_db():
    db = None
    f = open('/flash/database.db','r')
    content = f.read()
    print(content)
    if content:
        db = ujson.loads(content)
    f.close()
    return db

def clear_db():
    f = open('/flash/database.db','w')
    db = {}
    content = ujson.dumps(db)
    f.write(content)
    f.close()

class FaceDetectionNN(object):
    def __init__(self):

        self.object_detected = None
        self.percent = 0

        self.classes = ['face']
        self.anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
        self.x_center = 0
        self.y_center = 0

        self.object_detection_task = kpu.load(0x659000)
        a = kpu.set_outputs(self.object_detection_task, 0, 7, 7, 30)
        a = kpu.init_yolo2(self.object_detection_task, 0.1, 0.1, 5, self.anchor)

    def detect_objects(self, threshold, return_img=False):
        detected = False
        img = snapshot()

        img_copy = img.resize(224,224)
        a = img_copy.pix_to_ai()
        code = kpu.run_yolo2(self.object_detection_task, img_copy)

        if code:
            for i in code:
                if i.value() >= threshold:
                    detected = True

                    new_x, new_y = int(i.x()*1.07), int(i.y()*1.42)
                    roi = (new_x, new_y, int(i.w()*1.07),int(i.h()*1.42))
                    percent = i.value()
                    object_detected = self.classes[i.classid()]

                    if not return_img:
                        a=img.draw_rectangle(roi, color = (0x1c, 0xa2, 0xff), thickness=2)
                        a=img.draw_string(new_x, new_y-14, ("%s %%: %.2f" % (object_detected, percent)), color=(255,255,255), scale=1.5, mono_space=False)

            self.x_center, self.y_center, self.area, self.percent, roi  = _find_max(code)

        del(img_copy)

        if not detected:
            self.object_detected = None
            self.percent = -1
            if return_img:
                return img, None

        if return_img:
            return img, roi
        else:
            a = lcd.display(img)

        del(img)

    def get_detection_status(self, percent):
        threshold = percent/100
        self.detect_objects(threshold)
        if self.percent >= threshold:
            return True
        else:
            return False

    def get_detection_property(self, percent, argu):
        threshold = percent/100
        self.detect_objects(threshold)
        if self.percent >= threshold:
            if argu == 1:
                return self.x_center
            elif argu == 2:
                return self.y_center
            elif argu == 3:
                return self.area
        else:
            return -1

class LandmarksDetection(object):
    def __init__(self, detector):

        self.object_detected = None
        self.FaceDetector = detector
        self.landmark_task = kpu.load(0x6BD000)

        a = kpu.set_outputs(self.landmark_task, 0, 1, 1, 10)

    def detect_landmarks(self, threshold, return_img=False):

        img, roi = self.FaceDetector.detect_objects(threshold, True)
        self.kpts =[[-1,-1] for x in range(5)]

        if roi:

            face_cut = img.cut(*roi)
            face_cut_128 = face_cut.resize(128, 128)
            a = face_cut_128.pix_to_ai()
            fmap = kpu.forward(self.landmark_task, face_cut_128)
            plist = fmap[:]

            le = (roi[0] + int(plist[0] * roi[2]+5), roi[1] + int(plist[1] * roi[3]+5))
            re = (roi[0] + int(plist[2] * roi[2]), roi[1] + int(plist[3] * roi[3]+5))
            n = (roi[0] + int(plist[4] * roi[2]), roi[1] + int(plist[5] * roi[3]))
            lm = (roi[0] + int(plist[6] * roi[2]), roi[1] + int(plist[7] * roi[3]))
            rm = (roi[0] + int(plist[8] * roi[2]), roi[1] + int(plist[9] * roi[3]))
            self.kpts = [le, re, n, lm, rm]

            del(face_cut)
            del(face_cut_128)

            if return_img:
                return img, self.kpts, roi

            a = img.draw_cross(le[0], le[1], color=(0, 255, 0), size=5, thickness=3)
            a = img.draw_cross(re[0], re[1], color=(0, 255, 0), size=5, thickness=3)
            a = img.draw_cross(n[0], n[1], color=(0, 255, 0), size=5, thickness=3)
            a = img.draw_cross(lm[0], lm[1], color=(0, 255, 0), size=5, thickness=3)
            a = img.draw_cross(rm[0], rm[1], color=(0, 255, 0), size=5, thickness=3)

        a = lcd.display(img)

        return img, None, None

    def get_object_property(self, percent, landmark, xy):
        threshold = percent/100
        self.detect_landmarks(threshold)
        return self.kpts[landmark][xy]

class FaceRecognition(object):
    def __init__(self, lm_detector):

        self.id = -1
        self.max_score = 0
        self.threshold = 85
        self.LandmarkDetector = lm_detector

        self.db = _read_db()
        offset_x = 0
        offset_y = -15
        self.dst_point = [(44+offset_x, 59+offset_y),
                        (84+offset_x, 59+offset_y),
                        (64+offset_x, 82+offset_y),
                        (47+offset_x, 105),
                        (81+offset_x, 105)]

        self.img_face = image.Image(size=(128,128))
        a = self.img_face.pix_to_ai()

        self.fe_task = kpu.load(0x708000)
        a = kpu.set_outputs(self.fe_task, 0, 1, 1, 128)

    def compute_features(self, register = False):

        img, src_point, self.roi = self.LandmarkDetector.detect_landmarks(0.4, return_img=True)
        self.max_score = 0
        self.id = -1   
             
        if src_point:
            # align face to standard position
            a = img.pix_to_ai()

            T = image.get_affine_transform(src_point, self.dst_point)
            a = image.warp_affine_ai(img, self.img_face, T)
            a = self.img_face.ai_to_pix()

            if register:
                reg_img = image.Image('logo.jpg')
                a = reg_img.draw_image(self.img_face, (lcd.width()//2-68, lcd.height()//2-20))
                a = reg_img.draw_string(30, lcd.height()//2-48, "Registring face", color=(0,255,0), scale=2, mono_space=False)
                a = lcd.display(reg_img)
                del(reg_img)
                time.sleep(2)

            a = self.img_face.pix_to_ai()
            # calculate face feature vector
            fmap = kpu.forward(self.fe_task, self.img_face)
            #print(fmap[:])
            vector = list(map(lambda x:x/256, fmap[:]))
            self.feature = kpu.face_encode(vector)

            for id in self.db.keys():
                entry = _unhexlify(self.db[id]['vector'])
                score = kpu.face_compare(entry, self.feature)
                if score > self.max_score:
                    self.max_score = score
                    name = self.db[id]['name']
                    self.id = id

            if not self.max_score > self.threshold:
                name = 'Unknown'

                
            a=img.draw_rectangle(self.roi, color = (0x1c, 0xa2, 0xff), thickness=2)
            a=img.draw_string(self.roi[0], self.roi[1]-14, ("%s %%: %.2f" % (name, self.max_score)), color=(255,255,255), scale=1.5, mono_space=False)

            a = lcd.display(img)
            del(img)

    def is_ID(self, id, threshold):

        self.compute_features()
        self.threshold = threshold

        if self.id == id and self.max_score >= self.threshold:
            return True
        else:
            return False

    def get_recognition_results(self, threshold):

        self.compute_features()
        self.threshold = threshold

        if self.max_score >= self.threshold:
            return self.id
        else:
            return -1

    def get_recognition_property(self, id, threshold, argu):

        self.compute_features()
        self.threshold = threshold

        if self.id == id and self.max_score >= self.threshold:

            x_center = self.roi[0] + int(self.roi[2]/2)
            y_center = self.roi[1] + int(self.roi[3]/2)
            area = self.roi[2] * self.roi[3]

            if argu == 1:
                return x_center
            elif argu == 2:
                return y_center
            elif argu == 3:
                return area
        else:
            return -1

    def register_face(self, id, name):
        self.compute_features(register = True)
        self.db = _write_db(self.db, id, name, self.feature)
        print(self.db)

#clear_db()
#print(_read_db())
#ID = 0

#face_detection = FaceDetection()
#face_landmarks = LandmarksDetection(face_detection)
#face_recognition = FaceRecognition(face_landmarks)

#write_db(1, 'Dmitry', 'dfffd')
#write_db(2, 'Daniel', 'd12ffd')
#write_db(1, 'Kingsley', 'd12f213123fd')
#print(read_db())

#while True:
    #print(face_detection.get_detection_status(40))
    #print(face_detection.get_detection_property(40, 1))

    #print(face_landmarks.get_object_property(40, 0, 0))

    #print(face_recognition.is_ID(0, 80))
    #print(face_recognition.get_recognition_results(80))
    #print(face_recognition.get_recognition_property(0, 80, 1))

    #if not DigitalIn_button(17):
    #    face_recognition.register_face(ID, str(ID))
    #    ID += 1
    #    time.sleep(0.2)

