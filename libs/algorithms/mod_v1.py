import numpy as np
from libs.algorithms.intersection_finder import IntersectionFinder
from libs.commons.opencv_helpers import save_txt
import time

class MODv1:
    def __init__(self, cam, source_img, opt, save_path, det, img, names, w_ratio, h_ratio):
        self.cam = cam
        self.source_img = source_img
        self.opt = opt
        self.img = img
        self.save_path = save_path
        self.height, self.width, self.channels = img.shape
        self.det = det  # Original detected objects
        self.class_det = {}
        self.names = names
        self.w_ratio = w_ratio
        self.h_ratio = h_ratio
        self.detected_mbbox = []
        self.mbbox_img = None
        self.rgb_mbbox = [198, 50, 13]

    def run(self):
        # ts_extract = time.time()
        self.__extract()
        # t_extract = time.time() - ts_extract
        # print('\n**** Proc. Latency [extract img DATA]: (%.5fs)' % (t_extract))

        # Bug fixing: When unable to find both Person and Flag object, ignore
        if len(self.class_det) == 2:
            self.intersection = IntersectionFinder(self.opt, self.names, self.save_path, self.img, self.det,
                                                   self.class_det, self.width, self.height, self.w_ratio, self.h_ratio)
            self.intersection.find()
            self.detected_mbbox = self.intersection.get_mbbox_imgs()
            self.mbbox_img = self.intersection.get_img_with_mbbox()
            self.rgb_mbbox = self.intersection.get_rgb_mbbox()
            # print("Person-W-Flag object: %d founds." % len(detected_mbbox))
            print("Person=%d; Flag=%d; Person-W-Flag=%d;" % (len(self.class_det["Person"]), len(self.class_det["Flag"]),
                                                             len(self.detected_mbbox)))
        else:
            self.mbbox_img = self.img
            if self.opt.output_txt:
                save_txt(self.save_path, self.opt.txt_format)
            # print("Person + Flag objects NOT Found.")
            total_person = 0
            total_flag = 0
            if "Person" in self.class_det:
                total_person = len(self.class_det["Person"])
            if "Flag" in self.class_det:
                total_flag = len(self.class_det["Flag"])
            print("Person=%d; Flag=%d; Person-W-Flag=0;" % (total_person, total_flag))

    def get_mbbox_img(self):
        return self.mbbox_img

    def get_detected_mbbox(self):
        return self.detected_mbbox

    def get_rgb_mbbox(self):
        return self.rgb_mbbox

    '''
    FYI: Class label in this case (check in file `data/obj.names`):
        - class `Person` = 0; 
        - class `Flag` = 1; 
    '''

    def __extract(self):
        for c in self.det[:, -1].unique():
            self.class_det[self.names[int(c)]] = [i for i in range(len(self.det)) if self.det[i][-1] == c]
