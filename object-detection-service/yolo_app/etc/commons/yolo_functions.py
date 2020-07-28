from yolo_app.components.utils.utils import torch2numpy, get_current_time
from yolo_app.etc.commons.opencv_helpers import crop_image, np_xyxy2xywh, save_txt
import cv2
from datetime import datetime
import os


class YOLOFunctions:
    def __init__(self, opt):
        self.opt = opt
        self.__create_output_path()

    def __create_output_path(self):
        new_folder_name = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.raw_img_path = self.opt.output + "images_txt/" + new_folder_name + "/raw/"
        self.bbox_img_path = self.opt.output + "images_txt/" + new_folder_name + "/bbox/"
        self.crop_img_path = self.opt.output + "images_txt/" + new_folder_name + "/crop/"
        self.txt_bbox_path = self.opt.output + "images_txt/" + new_folder_name + "/txt/"

        # Make directories of out it
        os.makedirs(self.raw_img_path)
        os.makedirs(self.bbox_img_path)
        os.makedirs(self.crop_img_path)
        os.makedirs(self.txt_bbox_path)

    def _save_cropped_img(self, xyxy, im0, idx, cls, frame_id, ext):
        try:
            if self.opt.dump_crop_img:
                numpy_xyxy = torch2numpy(xyxy, int)
                xywh = np_xyxy2xywh(numpy_xyxy)
                crop_save_path = self.crop_img_path + "frame-%s_[cls=%s][idx=%s]%s" % (
                str(frame_id), str(idx), cls, ext)
                crop_image(crop_save_path, im0, xywh)
        except:
            print("\n[%s] Unable to perform crop image in frame-%s" % (get_current_time(), str(frame_id)))

    def _save_results(self, img, frame_id, is_raw=False):
        if self.opt.dump_bbox_img:
            if is_raw:
                print(" --- masuk IS RAW ...")
                frame_save_path = self.raw_img_path + "frame-%s.jpg" % str(frame_id)
                print(" --- RAW frame_save_path:", frame_save_path)
                if self.opt.dump_raw_img:
                    cv2.imwrite(frame_save_path, img)
            else:
                print(" --- masuk IS NOT RAW ...")
                frame_save_path = self.bbox_img_path + "frame-%s.jpg" % str(frame_id)

            cv2.imwrite(frame_save_path, img)

    def _safety_store_txt(self, xyxy, frame_id, cls, conf_score):
        try:
            txt_save_path = self.txt_bbox_path + "frame-%s" % str(frame_id)
            if self.opt.save_txt:
                save_txt(txt_save_path, self.opt.txt_format, bbox_xyxy=xyxy, cls=cls, conf=conf_score)
        except:
            print("\n[%s] Unable to perform crop image in frame-%s" % (get_current_time(), str(frame_id)))
