from libs.addons.redis.translator import redis_get, redis_set
from libs.addons.redis.my_redis import MyRedis
from utils.utils import *
import simplejson as json
from libs.settings import common_settings
from libs.algorithms.persistence_detection import PersistenceDetection
import time
# from datetime import datetime


class PIHLocationFetcher(MyRedis):
    # def __init__(self, opt, img, frame_id, total_pih_candidates, period_pih_candidates):
    def __init__(self, opt, img, drone_id, frame_id, raw_image):
        super().__init__()
        self.opt = opt
        self.img = img
        self.drone_id = drone_id
        self.frame_id = frame_id
        self.raw_image = raw_image

        # print(" >>>>>> drone_id:", drone_id)
        # print(" >>>>>> TYPE drone_id:", type(drone_id))
        self.key_total_pih_cand = "total-pih-candidates-" + str(drone_id)
        self.key_period_pih_cand = "period-pih-candidates-" + str(drone_id)

        # print(" \t ## key_total_pih_cand: ", self.key_total_pih_cand)
        # print(" \t ## key_period_pih_cand: ", self.key_period_pih_cand)

        # self.total_pih_candidates = total_pih_candidates
        self.total_pih_candidates = self.__get_total_pih_candidates()
        # self.period_pih_candidates = period_pih_candidates
        self.period_pih_candidates = self.__get_period_pih_candidates()

        self.gps_data = self.__get_gps_data()
        self.rgb_mbbox = common_settings["bbox_config"]["pih_color"]

        self.bbox_coord = []
        self.mbbox_coord = []

    def __get_total_pih_candidates(self):
        # print("@@@ __get_total_pih_candidates")
        total_pih_candidates = redis_get(self.rc_data, self.key_total_pih_cand)
        # print(" ### \t LOAD total_pih_candidates:", total_pih_candidates)
        # print(" ### \t LOAD total_pih_candidates TYPE:", type(total_pih_candidates))
        if total_pih_candidates is None:
            total_pih_candidates = 0
        # else:
        #     print(" ---- MASUK ELSE")
        #     total_pih_candidates = json.loads(total_pih_candidates)
        # print(">> total_pih_candidates:", total_pih_candidates)

        return total_pih_candidates

    def __get_period_pih_candidates(self):
        # print("@@@ __get_period_pih_candidates")
        period_pih_candidates = redis_get(self.rc_data, self.key_period_pih_cand)
        # print(" ### \t LOAD period_pih_candidates:", period_pih_candidates)
        # print(" ### \t LOAD period_pih_candidates TYPE:", type(period_pih_candidates))
        if period_pih_candidates is None:
            period_pih_candidates = []
        else:
            # print("MASUK ELSE ...")
            period_pih_candidates = json.loads(period_pih_candidates)
        # print(">> period_pih_candidates:", period_pih_candidates)

        return period_pih_candidates

    def __get_gps_data(self):
        gps_data = None
        while gps_data is None:
            key = "gps-data-" + str(self.drone_id)
            gps_data = redis_get(self.rc_gps, key)
            if gps_data is None:
                continue
            else:
                gps_data = json.loads(gps_data)
        return gps_data

    def __get_mbbox_coord(self):
        mbbox_data = None
        while mbbox_data is None:
            key = "d" + str(self.drone_id) + "-f" + str(self.frame_id) + "-mbbox"
            mbbox_data = redis_get(self.rc_bbox, key)
            if mbbox_data is None:
                continue
            else:
                mbbox_data = json.loads(mbbox_data)
        return mbbox_data

    def __get_bbox_coord(self):
        bbox_data = None
        while bbox_data is None:
            key = "d" + str(self.drone_id) + "-f" + str(self.frame_id) + "-bbox"
            bbox_data = redis_get(self.rc_bbox, key)
            # print(" $$$ bbox_data:", bbox_data, key)
            if bbox_data is None:
                continue
            else:
                bbox_data = json.loads(bbox_data)
        return bbox_data

    def run(self):
        # print(" ### @ RUN ... opt:", self.opt)
        if self.opt.plot_bbox:
            # print(" ~~~ self.opt.plot_bbox", self.opt.plot_bbox)
            self.bbox_coord = self.__get_bbox_coord()
            self.__plot_bbox()

        if self.opt.plot_mbbox:
            # print(" ~~~ self.opt.plot_mbbox", self.opt.plot_mbbox)
            self.mbbox_coord = self.__get_mbbox_coord()
            self.__plot_mbbox()

        # if self.opt.viewer_all_bbox:
        #     self.mbbox_coord = self.__get_mbbox_coord()
        #     self.__plot_mbbox()
        #
        #     self.bbox_coord = self.__get_bbox_coord()
        #     self.__plot_bbox()
        # elif self.opt.enable_mbbox:
        #     self.mbbox_coord = self.__get_mbbox_coord()
        #     self.__plot_mbbox()
        # elif self.opt.default_detection:
        #     self.bbox_coord = self.__get_bbox_coord()
        #     self.__plot_bbox()

        self.__update_total_pih_candidates()
        self.__update_period_pih_candidates()

    def __update_total_pih_candidates(self):
        redis_set(self.rc_data, self.key_total_pih_cand, self.total_pih_candidates)

    def __update_period_pih_candidates(self):
        p_data = json.dumps(self.period_pih_candidates)
        redis_set(self.rc_data, self.key_period_pih_cand, p_data)

    def __plot_bbox(self):
        t0_plot_bbox = time.time()
        if len(self.bbox_coord) > 0:  # MBBox exist!
            for data in self.bbox_coord:
                # obj_idx = data["obj_idx"]
                fl_bbox = [float(xyxy) for xyxy in data["xyxy"]]
                label = data["label"]
                color = [float(col) for col in data["color"]]
                plot_one_box(fl_bbox, self.img, label=label, color=color)  # plot bbox

        t_plot_bbox = time.time() - t0_plot_bbox
        print("Latency [Plot YOLOv3 BBox] of frame-%d: (%.5fs)" % (self.frame_id, t_plot_bbox))

    def __plot_mbbox(self):
        t0_plot_mbbox = time.time()
        if len(self.mbbox_coord) > 0:  # MBBox exist!
            t0_pers_det = time.time()
            self.total_pih_candidates += 1
            self.period_pih_candidates.append(int(self.frame_id))
            pers_det = PersistenceDetection(self.opt, self.frame_id, self.total_pih_candidates,
                                            self.period_pih_candidates)
            self.__maintaince_period_pih_cand(pers_det.get_persistence_window())

            # Get Latency of [Persistance Detection]
            t_pers_det = time.time() - t0_pers_det
            print("Latency [Persistance Detection] of frame-%d: (%.5fs)" % (self.frame_id, t_pers_det))

            pers_det.run()
            selected_label = pers_det.get_label()

            for data in self.mbbox_coord:
                # obj_idx = data["obj_idx"]
                fl_mbbox = [float(xyxy) for xyxy in data["xyxy"]]
                plot_one_box(fl_mbbox, self.img, label=selected_label, color=self.rgb_mbbox)  # plot bbox

        t_plot_mbbox = time.time() - t0_plot_mbbox
        print("Latency [Plot MBBox] of frame-%d: (%.5fs)" % (self.frame_id, t_plot_mbbox))

    def __maintaince_period_pih_cand(self, persistence_window):
        if len(self.period_pih_candidates) > persistence_window:
            self.period_pih_candidates.pop(0)

    def get_bbox(self):
        return self.bbox_coord

    def get_mbbox(self):
        return self.mbbox_coord

    def get_mbbox_img(self):
        return self.img

    # def get_total_pih_candidates(self):
    #     return self.total_pih_candidates
    #
    # def get_period_pih_candidates(self):
    #     return self.period_pih_candidates
