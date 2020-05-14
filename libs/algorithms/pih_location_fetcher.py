from libs.addons.redis.translator import redis_get, redis_set
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.utils import get_gps_data, get_visualizer_fps
from utils.utils import *
import simplejson as json
from libs.settings import common_settings
from libs.algorithms.persistence_detection import PersistenceDetection
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

        self.gps_data = self.__get_gps_data()
        self.rgb_mbbox = common_settings["bbox_config"]["pih_color"]

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
        self.__plot_fps_info(img_width)
        self.__plot_gps_info(img_height)

        self.__update_total_pih_candidates()
        self.__update_period_pih_candidates()

    def __update_total_pih_candidates(self):
        redis_set(self.rc_data, self.key_total_pih_cand, self.total_pih_candidates)

    def __update_period_pih_candidates(self):
        p_data = json.dumps(self.period_pih_candidates)
        redis_set(self.rc_data, self.key_period_pih_cand, p_data)

    def __plot_fps_info(self, img_width):
        x_coord, y_coord = (img_width - 150), 30
        # visualizer_fps = get_visualizer_fps(self.rc_latency, self.drone_id)

        # t0_frame_key = "t0-frame-" + str(self.drone_id) + "-" + str(self.frame_id)
        t_start_key = "start-" + str(self.drone_id)
        # t0 = redis_get(self.rc_latency, t0_frame_key)
        t0 = redis_get(self.rc_latency, t_start_key)
        # t1 = time.time()
        t1 = time.time()
        t_elapsed = t1 - t0
        visualizer_fps = int(self.frame_id) / t_elapsed

        fps_visualizer_key = "fps-visualizer-%s" % str(self.drone_id)
        redis_set(self.rc_latency, fps_visualizer_key, visualizer_fps)

        # visualizer_fps = 1.0 / (t1 - t0)

        # Set labels
        if visualizer_fps is None:
            label = "FPS: None"
        else:
            label = "FPS: %.2f" % visualizer_fps

        # Add filled box
        tl = round(0.002 * (self.img.shape[0] + self.img.shape[1]) / 2) + 1  # line thickness
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c1 = (int(x_coord), int(y_coord))
        c2 = x_coord + t_size[0], y_coord - t_size[1] - 3
        cv2.rectangle(self.img, c1, c2, [0, 0, 0], -1)  # filled

        cv2.putText(self.img, label, (x_coord, y_coord), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    def __plot_gps_info(self, img_height):
        x_coord_lbl, y_coord_lbl = 10, (img_height - 90)
        x_coord_gps, y_coord_gps = 10, (img_height - 60)
        x_coord_obj, y_coord_obj = 10, (img_height - 30)
        gps_data = get_gps_data(self.rc_gps, self.drone_id)
        gps_ts = time.strftime('%H:%M:%S', time.localtime(gps_data["timestamp"]))
        long = gps_data["gps"]["long"]
        lat = gps_data["gps"]["lat"]
        alt = gps_data["gps"]["alt"]

        # Set labels
        gps_title_label = "GPS Information (%s):" % gps_ts
        gps_data_label = "LONG= %f; LAT= %f; ALT= %f;" % (long, lat, alt)
        obj_data_label = "Detection status: %s" % self.det_status

        # Add filled box
        tl = round(0.002 * (self.img.shape[0] + self.img.shape[1]) / 2) + 1  # line thickness
        tf = max(tl - 1, 1)  # font thickness
        t_size_title = cv2.getTextSize(gps_data_label, 0, fontScale=tl / 3, thickness=tf)[0]
        t_size = cv2.getTextSize(gps_data_label, 0, fontScale=tl / 3, thickness=tf)[0]
        t_size_obj = cv2.getTextSize(gps_data_label, 0, fontScale=tl / 3, thickness=tf)[0]
        c1 = (int(x_coord_lbl), int(y_coord_lbl - 30))
        c2 = x_coord_obj + t_size_title[0] - 300, y_coord_obj - t_size_obj[1] + 40

        cv2.rectangle(self.img, c1, c2, [0, 0, 0], -1)  # filled

        cv2.putText(self.img, gps_title_label,
                    (x_coord_lbl, y_coord_lbl), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        cv2.putText(self.img, gps_data_label,
                    (x_coord_gps, y_coord_gps), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        # Plot detection status
        cv2.putText(self.img, obj_data_label,
                    (x_coord_obj, y_coord_obj), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

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
            self.selected_label = pers_det.get_label()
            self.det_status = pers_det.get_det_status()

            for data in self.mbbox_coord:
                # obj_idx = data["obj_idx"]
                fl_mbbox = [float(xyxy) for xyxy in data["xyxy"]]
                plot_one_box(fl_mbbox, self.img, label=self.selected_label, color=self.rgb_mbbox)  # plot bbox

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
