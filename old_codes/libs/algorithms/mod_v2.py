import numpy as np
# from libs.algorithms.intersection_finder import IntersectionFinder
from libs.commons.opencv_helpers import save_txt
import time
from libs.algorithms.region_cluster import RegionCluster
from libs.commons.util import find_point
from libs.commons.opencv_helpers import get_det_xyxy, np_xyxy2xywh, get_mbbox, np_xyxy2centroid, get_xyxy_distance_manhattan, get_xyxy_distance, save_txt
from utils.utils import plot_one_box
from libs.settings import common_settings


class MODv2(RegionCluster):
    def __init__(self, cam, source_img, opt, save_path, det, img, names):
        super().__init__()
        self.cam = cam
        self.source_img = source_img
        self.opt = opt
        self.img = img
        self.mbbox_img = img.copy()
        self.save_path = save_path
        self.height, self.width, self.channels = img.shape
        self.det = det  # Original detected objects
        self.class_det = {"Person": [], "Flag": []}
        self.names = names
        self.detected_mbbox = []
        self.pih_label = common_settings["bbox_config"]["pih_label"]
        self.rgb_mbbox = common_settings["bbox_config"]["pih_color"]
        self.paired_flags = {}
        self.saved_dist = {}  # of (FlagID, PersonID), e.g. ["0-0"] = 80

        self.person_xyxys = {}
        self.flag_xyxys = {}
        self.flag_pair_candidates = {}

    def run(self):
        self.__extract()

        if self.__is_eligible():
            self.map_to_clusters()
            self.find_pair_candidates()
            self.pair_selection()

    def __is_flag_valid(self, flag_idx, person_idx):
        person_xyxy = get_det_xyxy(self.det[person_idx])
        flag_xyxy = get_det_xyxy(self.det[flag_idx])

        person_xywh = np_xyxy2xywh(person_xyxy)
        flag_xywh = np_xyxy2xywh(flag_xyxy)
        # print(" -------- person_xywh VS flag_xywh:", person_xywh, flag_xywh)
        if flag_xywh[3] > person_xywh[3]:
            return False
        return True

    def __is_distance_valid(self, dist_idx):
        dist_th = 450.0
        if self.saved_dist[dist_idx] < dist_th:
            return True
        return False

    def find_pair_candidates(self):
        for cluster_data in self.mapped_obj:
            if len(cluster_data["Person"]) > 0 and len(cluster_data["Flag"]) > 0:
                for flag_idx in cluster_data["Flag"]:
                    for person_idx in cluster_data["Person"]:
                        dist_idx = str(flag_idx) + "-" + str(person_idx)

                        if self.__is_flag_valid(flag_idx, person_idx) and self.__is_distance_valid(dist_idx):
                            if person_idx not in self.flag_pair_candidates[flag_idx]["id"]:
                                self.flag_pair_candidates[flag_idx]["id"].append(person_idx)
                                # dist_idx = str(flag_idx) + "-" + str(person_idx)
                                self.flag_pair_candidates[flag_idx]["dist"].append(self.saved_dist[dist_idx])

    def pair_selection(self):
        for flag_idx, pair_data in self.flag_pair_candidates.items():
            if len(pair_data["id"]) > 0:
                selected_idx = pair_data["dist"].index(min(pair_data["dist"]))
                selected_person_idx = pair_data["id"][selected_idx]

                person_xyxy = get_det_xyxy(self.det[selected_person_idx])
                flag_xyxy = get_det_xyxy(self.det[flag_idx])
                mbbox_xyxy = get_mbbox(person_xyxy, flag_xyxy)

                self.detected_mbbox.append(mbbox_xyxy)
                plot_one_box(mbbox_xyxy, self.mbbox_img, label=self.pih_label, color=self.rgb_mbbox)

    def __is_eligible(self):
        if "Person" not in self.class_det or "Flag" not in self.class_det:
            return False
        else:
            return True

    def map_to_clusters(self):
        for person_idx in self.class_det["Person"]:
            person_xyxy = get_det_xyxy(self.det[person_idx])
            person_centroid = np_xyxy2centroid(person_xyxy)
            self.person_xyxys[person_idx] = [person_idx, person_xyxy, person_centroid]
            self.find_cluster(person_centroid, "Person", person_idx)

        for flag_idx in self.class_det["Flag"]:
            flag_xyxy = get_det_xyxy(self.det[flag_idx])
            flag_centroid = np_xyxy2centroid(flag_xyxy)
            self.flag_xyxys[flag_idx] = [flag_idx, flag_xyxy, flag_centroid]

            self.save_distance(flag_idx, flag_centroid)
            self.flag_pair_candidates[flag_idx] = {"id": [], "dist": []}

            self.find_cluster(flag_centroid, "Flag", flag_idx)

    def save_distance(self, flag_idx, centroid):
        i = 0
        for person_idx, person_data in self.person_xyxys.items():
            distance = get_xyxy_distance(centroid, person_data[2])
            # print(" ------------ distance: ", distance)
            dist_idx = str(flag_idx) + "-" + str(person_idx)
            self.saved_dist[dist_idx] = distance
            i += 1

    def find_cluster(self, centroid, cls, obj_idx):
        for i in range (len(self.region_xyxy)):
            reg_xyxy = self.region_xyxy[i][0]
            selected_regions = self.region_xyxy[i][1]
            if find_point(reg_xyxy, centroid):
                self.map(selected_regions, cls, obj_idx)

    def map(self, selected_regions, cls, obj_idx):
        for cluster_idx in selected_regions:
            self.mapped_obj[cluster_idx][cls].append(obj_idx)

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
        idx_detected = 0
        for *xyxy, conf, cls in self.det:
            self.class_det[self.names[int(cls)]].append(idx_detected)
            idx_detected += 1
