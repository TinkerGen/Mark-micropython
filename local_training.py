from camera import snapshot, global_value, rows
import image, lcd, time
import KPU as kpu
import gc
import ujson

dict_add = {}
class OnDeviceTraining(object):
    def __init__(self, categoryname=[], samplesnumber=15, bool=False):
        self.row = global_value.row
        global_value.row = global_value.row + 1
        try:
            del self.model
        except Exception:
            pass
        try:
            del self.classifier
        except Exception:
            pass

        self.classnumber = len(categoryname)
        self.samplesnumber = samplesnumber
        self.categoryname = categoryname
        self.img_copy = None
        self.cap_num = 0
        self.train_status = 0
        self.class_list=[]
        self.percent = 0
        self.image_class = 0
        
        if bool:
            self.model = kpu.load(0x800000)
            self.classifier = kpu.classifier(self.model, self.classnumber, self.samplesnumber)
        else:
            pass    
    
    def classify_image(self, string):
        img = snapshot()
        self.img_copy = img.resize(224,224)
        a = self.img_copy.pix_to_ai()
        a = img.draw_string(0, rows[self.row], string, color=(255,255,255), scale=1.5, mono_space=False)
        a = lcd.display(img)
        del(img)
        gc.collect()

    # parameter 1-5
    def record_seed_sample(self, parameter=''):
        self.classify_image(("Image for %s is taken" % parameter))
        if self.cap_num < self.classnumber:
            class_index = self.categoryname.index(parameter)
            index = self.classifier.add_class_img(self.img_copy)
            self.cap_num += 1
            self.class_list.append(class_index)

    def record_samples_training(self):
        self.classify_image(("Samples taken: %d" % (self.cap_num-3)))
        if self.cap_num < self.classnumber + self.samplesnumber:
            index = self.classifier.add_sample_img(self.img_copy)
            self.cap_num += 1

        if self.train_status == 0:
            if self.cap_num >= self.classnumber + self.samplesnumber:
                print("start train")
                img = snapshot()
                a = img.draw_string(lcd.width()//2-68,lcd.height()//2-4, "Training...", color=(0,255,0), scale=3, mono_space=False)
                lcd.display(img)
                del(img)
                #del(self.img_copy)
                gc.collect()
                time.sleep(2)
                self.classifier.train()
                print("train end")
                self.train_status = 1

    def class_predict(self, THRESHOLD=50):
        img = snapshot()
        self.img_copy = img.resize(224,224)
        #kpu.memtest()
        a = self.img_copy.pix_to_ai()
        res_index = -1
        try:
            res_index, min_dist = self.classifier.predict(self.img_copy)
            self.percent = round(min_dist, 0)
            #print(" percent:",self.percent)
            #print("res_index: ", res_index)
            #print("{:.2f}".format(min_dist))
        except Exception as e:
            print("predict err:", e)
        if res_index >= 0 and self.percent >= THRESHOLD :
            self.image_class = self.categoryname[self.class_list[res_index]]
            #print("predict result:", self.image_class)

        a = lcd.display(img)
        del(img)
        #del(img_copy)
        gc.collect()

    def save_model_file(self, filename=''):
        self.classifier.save(filename)
        #print(filename.split('.')[0]+".names")
        f = open(filename.split('.')[0]+".names",'w')
        #print(str(self.class_list))
        f.write(str(self.class_list))
        f.close()

    def load_model_file(self, filename=''):
        self.model = kpu.load(0x800000)
        classifier = kpu.classifier.load(self.model, filename)
        self.classifier = classifier[0]
        f = open(filename.split('.')[0]+'.names','r')
        self.class_list = ujson.loads(f.read())
        #print(self.class_list)
        f.close()

    def get_classification_result(self, percent):
        threshold = percent/100
        self.class_predict(threshold)
        #gc.collect()
        if self.percent >= threshold:
            return self.image_class
        else:
            return -1

    def is_class(self, _class, percent):
        threshold = percent/100
        self.class_predict(threshold)
        #gc.collect()
        if self.image_class == _class and self.percent >= threshold:
            return True
        else:
            return False


"""
filename = "/sd/123.tg"
categoryname = ['a', 'b', 'c']
samplesnumber = 15 #15-25

modeltrain = OnDeviceTraining(categoryname, samplesnumber, 1)
time.sleep(4)
modeltrain.record_seed_sample(categoryname[2])
time.sleep(4)
modeltrain.record_seed_sample(categoryname[1])
time.sleep(4)
modeltrain.record_seed_sample(categoryname[0])
time.sleep(4)

for a in range(15):
    modeltrain.record_samples_training()
    time.sleep(3)



modeltrain.save_model_file(filename)
#modeltrain.load_model_file(filename)

while True:
    pass
    #modeltrain.get_classification_result(50)
    modeltrain.is_class('a', 20)

"""



