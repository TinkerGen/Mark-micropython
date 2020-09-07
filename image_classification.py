from camera import snapshot, global_value, rows
import image, lcd, time
import KPU as kpu
import gc

class ImageClassification(object):
    def __init__(self, FileName, Label, bool=False):
        self.row = global_value.row
        global_value.row = global_value.row + 1
        self.percent = 0
        self.image_class = 0
        self.file_name = FileName
        self.labels = Label
        if bool:
            self.image_objects_task = kpu.load(self.file_name)
            a = kpu.set_outputs(self.image_objects_task, 0, 1, 1, len(self.labels))
        else:
            pass    

    def classify_image(self, threshold):
        img = snapshot()
        img_copy = img.resize(224,224)
        a = img_copy.pix_to_ai()
        fmap = kpu.forward(self.image_objects_task, img_copy)
        plist=fmap[:]
        pmax=max(plist)
        self.percent = pmax
        if self.percent >= threshold:
            max_index=plist.index(pmax)
            a = img.draw_string(8, rows[self.row], ("Result: %s %%: %.2f" % (self.labels[max_index].strip(), pmax)), color=(255,255,255), scale=1.5, mono_space=False)
            self.image_class = self.labels[max_index].strip()
        a = lcd.display(img)
        del(img)
        del(img_copy)

    def get_classification_result(self, percent):
        threshold = percent/100
        self.classify_image(threshold)
        if self.percent >= threshold:
            return self.image_class
        else:
            return -1

    def is_class(self, _class, percent):
        threshold = percent/100
        self.classify_image(threshold)
        gc.collect()
        if self.image_class == _class and self.percent >= threshold:
            return True
        else:
            return False
'''
# file_name : flash 0x200000  SD-card "/sd/xxx.kmodel"
# labels: []
common_filename = 0x200000
#common_filename = "/sd/common_10.kmodel"
common_labels = ['backpack', 'bomb', 'book', 'chair', 'computer', 'cup_mug', 'pen','person', 'pizza', 'smartphone']

domestic_filename = 0x300000
domestic_labels = ['background', 'bird', 'cat', 'dog', 'hedgehog', 'mouse']

zoo_filename = 0x500000
zoo_labels = ['alligator', 'background', 'bear', 'elephant', 'giraffe', 'tiger']


#common_objects = ImageClassification(common_filename, common_labels, 1)
domestic_animals = ImageClassification(domestic_filename, domestic_labels, 1)
zoo_animals = ImageClassification(zoo_filename, zoo_labels, 1)

while True:
    #common_objects.get_classification_result(50)
    #common_objects.is_class('person', 50)

    domestic_animals.get_classification_result(50)
    #domestic_animals.is_class('cat', 50)
  
    zoo_animals.get_classification_result(50)
    #zoo_animals.is_class('tiger', 50)
'''
