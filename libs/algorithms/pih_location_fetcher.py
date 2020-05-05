from libs.addons.redis.translator import redis_get
from libs.addons.redis.my_redis import MyRedis
from utils.utils import *
import simplejson as json
from libs.settings import common_settings


class PIHLocationFetcher(MyRedis):
    def __init__(self, opt, img, frame_id):
        super().__init__()
        self.opt = opt
        self.img = img
        self.frame_id = frame_id
        self.gps_data = self.__get_gps_data()
        self.pih_label = common_settings["bbox_config"]["pih_label"]
        self.rgb_mbbox = common_settings["bbox_config"]["pih_color"]

    def __get_gps_data(self):
        gps_data = None
        while gps_data is None:
            key = "gps-data-" + str(self.opt.drone_id)
            gps_data = redis_get(self.rc_gps, key)
            if gps_data is None:
                continue
            else:
                gps_data = json.loads(gps_data)
        return gps_data

    def __get_mbbox_coord(self):
        mbbox_data = None
        while mbbox_data is None:
            key = "d" + str(self.opt.drone_id) + "-f" + str(self.frame_id) + "-mbbox"
            mbbox_data = redis_get(self.rc_bbox, key)
            if mbbox_data is None:
                continue
            else:
                mbbox_data = json.loads(mbbox_data)
        return mbbox_data

    def __get_bbox_coord(self):
        bbox_data = None
        while bbox_data is None:
            key = "d" + str(self.opt.drone_id) + "-f" + str(self.frame_id) + "-bbox"
            bbox_data = redis_get(self.rc_bbox, key)
            if bbox_data is None:
                continue
            else:
                bbox_data = json.loads(bbox_data)
        return bbox_data

    def run(self):
        if self.opt.enable_mbbox:
            self.mbbox_coord = self.__get_mbbox_coord()
            self.__plot_mbbox()
        elif self.opt.default_detection:
            self.bbox_coord = self.__get_bbox_coord()
            self.__plot_bbox()

    def __plot_bbox(self):
        if len(self.bbox_coord) > 0:  # MBBox exist!
            for data in self.bbox_coord:
                # obj_idx = data["obj_idx"]
                fl_bbox = [float(xyxy) for xyxy in data["xyxy"]]
                label = data["label"]
                color = [float(col) for col in data["color"]]
                plot_one_box(fl_bbox, self.img, label=label, color=color)  # plot bbox

    def __plot_mbbox(self):
        if len(self.mbbox_coord) > 0:  # MBBox exist!
            for data in self.mbbox_coord:
                # obj_idx = data["obj_idx"]
                fl_mbbox = [float(xyxy) for xyxy in data["xyxy"]]
                plot_one_box(fl_mbbox, self.img, label=self.pih_label, color=self.rgb_mbbox)  # plot bbox

    def get_mbbox(self):
        return self.mbbox_coord

    def get_mbbox_img(self):
        return self.img
