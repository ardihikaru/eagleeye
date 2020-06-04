from libs.addons.redis.translator import redis_get, redis_set
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.utils import get_gps_data, get_visualizer_fps
from utils.utils import *
import simplejson as json
from libs.settings import common_settings
from libs.algorithms.persistence_detection import PersistenceDetection
from libs.addons.gps_collector.gps_sender import GPSSender
import time


class PIHLocationFetcher(MyRedis):
    def __init__(self, opt, img, drone_id, frame_id, raw_image, visual_type):
        super().__init__()
        self.opt = opt
        self.img = img
        self.drone_id = drone_id
        self.frame_id = frame_id
        self.raw_image = raw_image
        self.visual_type = visual_type
        self.selected_label = common_settings["bbox_config"]["pih_label"]  # default
        self.det_status = "No " + common_settings["bbox_config"]["pih_label"] + " is detected."

        self.key_total_pih_cand = "total-pih-candidates-" + str(drone_id)
        self.key_period_pih_cand = "period-pih-candidates-" + str(drone_id)

        self.total_pih_candidates = self.__get_total_pih_candidates()
        self.period_pih_candidates = self.__get_period_pih_candidates()

        # self.gps_data = self.__get_gps_data()
        self.gps_data = get_gps_data(self.rc_gps, drone_id)
        self.rgb_pih = common_settings["bbox_config"]["pih_color"]
        self.rgb_person = common_settings["bbox_config"]["person_color"]
        self.rgb_flag = common_settings["bbox_config"]["flag_color"]

        self.bbox_coord = []
        self.mbbox_coord = []

    def __get_total_pih_candidates(self):
        total_pih_candidates = redis_get(self.rc_data, self.key_total_pih_cand)
        if total_pih_candidates is None:
            total_pih_candidates = 0

        return total_pih_candidates

    def __get_period_pih_candidates(self):
        period_pih_candidates = redis_get(self.rc_data, self.key_period_pih_cand)
        if period_pih_candidates is None:
            period_pih_candidates = []
        else:
            period_pih_candidates = json.loads(period_pih_candidates)

        return period_pih_candidates

    # def __get_gps_data(self):
    #     gps_data = None
    #     while gps_data is None:
    #         key = "gps-data-" + str(self.drone_id)
    #         gps_data = redis_get(self.rc_gps, key)
    #         if gps_data is None:
    #             continue
    #         else:
    #             gps_data = json.loads(gps_data)
    #     return gps_data

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
            if bbox_data is None:
                continue
            else:
                bbox_data = json.loads(bbox_data)
        return bbox_data

    def run(self):
        if self.visual_type == 3:
            self.bbox_coord = self.__get_bbox_coord()
            self.__plot_bbox()

            self.mbbox_coord = self.__get_mbbox_coord()
            self.__plot_mbbox()
        elif self.visual_type == 2:
            self.mbbox_coord = self.__get_mbbox_coord()
            self.__plot_mbbox()
        elif self.visual_type == 1:
            self.bbox_coord = self.__get_bbox_coord()
            self.__plot_bbox()

        img_height, img_width, _ = self.img.shape
        # self.__plot_fps_info(img_width)
        self.img = plot_fps_info(img_width, self.drone_id, self.frame_id, self.rc_latency, self.img, redis_set,
                                 redis_get, store_fps=True)
        # self.__plot_gps_info(img_height, self.gps_data, self.det_status, self.img)
        # plot_gps_info(img_height, self.gps_data, self.det_status, self.img)
        plot_gps_info(img_height, self.gps_data, self.det_status, self.img)

        self.__update_total_pih_candidates()
        self.__update_period_pih_candidates()

    def __update_total_pih_candidates(self):
        redis_set(self.rc_data, self.key_total_pih_cand, self.total_pih_candidates)

    def __update_period_pih_candidates(self):
        p_data = json.dumps(self.period_pih_candidates)
        redis_set(self.rc_data, self.key_period_pih_cand, p_data)

    def __clean_label(self, old_label):
        arr = old_label.split(" ")
        # return arr[0] + " - " + arr[1]
        return arr[0]

    def __get_color(self, label, data):
        if label.lower() == "person":
            return self.rgb_person
        elif label.lower() == "flag":
            return self.rgb_flag
        else:
            return [float(col) for col in data["color"]]

    def __plot_bbox(self):
        t0_plot_bbox = time.time()
        if len(self.bbox_coord) > 0:  # MBBox exist!
            for data in self.bbox_coord:
                # obj_idx = data["obj_idx"]
                fl_bbox = [float(xyxy) for xyxy in data["xyxy"]]
                # label = data["label"]
                label = self.__clean_label(data["label"])
                # color = [float(col) for col in data["color"]]
                color = self.__get_color(label, data)
                plot_one_box(fl_bbox, self.img, label=label, color=color)  # plot bbox

        t_plot_bbox = time.time() - t0_plot_bbox
        # print("Latency [Plot YOLOv3 BBox] of frame-%d: (%.5fs)" % (self.frame_id, t_plot_bbox))

    def __plot_mbbox(self):
        t0_plot_mbbox = time.time()
        if len(self.mbbox_coord) > 0:  # MBBox exist!

            long = self.gps_data["gps"]["long"]
            lat = self.gps_data["gps"]["lat"]
            alt = self.gps_data["gps"]["alt"]

            print("[%s] PiH FOUND at frame-%d (Long=%s; Lat=%s; Alt=%s)\n" %
                  (get_current_time(), int(self.frame_id), str(long), str(lat), str(alt)))
            t0_pers_det = time.time()
            self.total_pih_candidates += 1
            self.period_pih_candidates.append(int(self.frame_id))

            pers_det = PersistenceDetection(self.opt, self.frame_id, self.total_pih_candidates,
                                            self.period_pih_candidates)
            self.__maintaince_period_pih_cand(pers_det.get_persistence_window())

            # Get Latency of [Persistance Detection]
            # t_pers_det = time.time() - t0_pers_det
            # print("Latency [Persistance Detection] of frame-%d: (%.5fs)" % (self.frame_id, t_pers_det))

            pers_det.run()
            self.selected_label = pers_det.get_label()
            self.det_status = pers_det.get_det_status()

            # TBD:
            # 1. Send this function asynchronously
            # 2. Only send 1 time per second
            # GPSSender(self.opt, self.drone_id).send_gps_data()

            for data in self.mbbox_coord:
                fl_mbbox = [float(xyxy) for xyxy in data["xyxy"]]
                plot_one_box(fl_mbbox, self.img, label=self.selected_label, color=self.rgb_pih)  # plot bbox

        t_plot_mbbox = time.time() - t0_plot_mbbox
        # print("Latency [Plot MBBox] of frame-%d: (%.5fs)" % (self.frame_id, t_plot_mbbox))

    def __maintaince_period_pih_cand(self, persistence_window):
        if len(self.period_pih_candidates) > persistence_window:
            self.period_pih_candidates.pop(0)

    def get_bbox(self):
        return self.bbox_coord

    def get_mbbox(self):
        return self.mbbox_coord

    def get_mbbox_img(self):
        return self.img
