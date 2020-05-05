from libs.addons.redis.translator import redis_get, redis_set
from libs.addons.redis.my_redis import MyRedis
from utils.utils import *
import simplejson as json


class PIHLocationFetcher(MyRedis):
    def __init__(self, opt, img, frame_id):
        # print(" ~~~~~~~~~~~ frame_id = ", frame_id)
        super().__init__()
        self.opt = opt
        self.img = img
        self.frame_id = frame_id
        self.gps_data = self.__get_gps_data()
        self.mbbox_coord = self.__get_mbbox_coord()
        # try:
        #     self.mbbox_coord = self.__get_mbbox_coord()
        # except Exception as e:
        #     print(" ---------- GAK NEMU ...")
        self.rgb_mbbox = [198, 50, 13]
        self.label_mbbox = "PiH"
        # print(" --- SELESAI")

    # TBD
    def __get_gps_data(self):
        return False

    def __get_mbbox_coord(self):
        # is_empty = True
        mbbox_data = None
        while mbbox_data is None:
            key = str(self.opt.drone_id) + "-" + str(self.frame_id)
            # print(" #### Looking @ key store MBBox = ", key)
            mbbox_data = redis_get(self.rc_bbox, key)
            # print(" ---- mbbox_data:", mbbox_data)
            if mbbox_data is None:
                continue
            else:
                # print(" ---- mbbox_data: ", mbbox_data)
                mbbox_data = json.loads(mbbox_data)
                # if len(mbbox_data) == 0:
                #     mbbox_data = None
                # print(" ##### Captured MBBox: ", mbbox_data)
                # print(" ##### Captured MBBox: ", type(mbbox_data))
                # is_empty = False
        return mbbox_data

    def run(self):
        # print(" ### len(self.mbbox_coord) :", len(self.mbbox_coord))
        if len(self.mbbox_coord) > 0:  # MBBox exist!
            for frame_id, mbbox in self.mbbox_coord.items():
                # print(" ## frame_id, mbbox = ", frame_id, mbbox)
                fl_mbbox = [float(xy) for xy in mbbox]
                # print(" ### fl_mbbox = ", fl_mbbox)
                plot_one_box(fl_mbbox, self.img, label=self.label_mbbox, color=self.rgb_mbbox)  # plot bbox

    def get_mbbox(self):
        return self.mbbox_coord

    def get_mbbox_img(self):
        return self.img
