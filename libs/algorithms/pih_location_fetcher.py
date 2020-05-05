from libs.addons.redis.translator import redis_get
from libs.addons.redis.my_redis import MyRedis
from utils.utils import *
import simplejson as json


class PIHLocationFetcher(MyRedis):
    def __init__(self, opt, img, frame_id):
        super().__init__()
        self.opt = opt
        self.img = img
        self.frame_id = frame_id
        self.gps_data = self.__get_gps_data()
        self.mbbox_coord = self.__get_mbbox_coord()
        self.rgb_mbbox = [198, 50, 13]
        self.label_mbbox = "PiH"

    # TBD
    def __get_gps_data(self):
        return False

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

    def run(self):
        if len(self.mbbox_coord) > 0:  # MBBox exist!
            for frame_id, mbbox in self.mbbox_coord.items():
                fl_mbbox = [float(xy) for xy in mbbox]
                plot_one_box(fl_mbbox, self.img, label=self.label_mbbox, color=self.rgb_mbbox)  # plot bbox

    def get_mbbox(self):
        return self.mbbox_coord

    def get_mbbox_img(self):
        return self.img
