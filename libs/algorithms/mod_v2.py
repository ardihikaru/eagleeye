import numpy as np
# from libs.algorithms.intersection_finder import IntersectionFinder
from libs.commons.opencv_helpers import save_txt
import time
from libs.algorithms.region_cluster import RegionCluster
from libs.commons.util import find_point
from libs.commons.opencv_helpers import get_det_xyxy, np_xyxy2xywh, get_mbbox, np_xyxy2centroid, get_xyxy_distance_manhattan, get_xyxy_distance, save_txt
from utils.utils import plot_one_box

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
        # self.class_det = {}
        self.class_det = {"Person": [], "Flag": []}
        self.names = names
        self.detected_mbbox = []
        # self.mbbox_img = None
        self.rgb_mbbox = [198, 50, 13]
        self.paired_flags = {}
        self.saved_dist = {} # of (FlagID, PersonID), e.g. ["0-0"] = 80

        # self.person_xyxys = []
        # self.flag_xyxys = []
        self.person_xyxys = {}
        self.flag_xyxys = {}
        self.flag_pair_candidates = {}

    def run(self):
        ts_extract = time.time()
        self.__extract()
        t_extract = time.time() - ts_extract
        # print('\n**** Proc. Latency [extract img DATA]: (%.5fs)' % t_extract)

        if self.__is_eligible():
            ts_map2cluster = time.time()
            self.map_to_clusters()
            t_map2cluster = time.time() - ts_map2cluster
            # print('\n**** Proc. Latency [Map to Clusters]: (%.5fs)' % t_map2cluster)
            # print("###### FINISHED MAPPING ##### Mapped object:", self.mapped_obj)
            # print("###### FINISHED saved_dist ##### saved_dist:", self.saved_dist)

            self.find_pair_candidates()
            # print("###### FINISHED find_pair_candidates ##### flag_pair_candidates:", self.flag_pair_candidates)
            self.pair_selection()
        # else:
        #     if self.opt.output_txt:
        #         save_txt(self.save_path, self.opt.txt_format)
                # save_txt(self.save_path, self.opt.txt_format, "")
        # print("########### isi class", self.class_det)

    def find_pair_candidates(self):
        for cluster_data in self.mapped_obj:
            # print("### Cluster Data:", cluster_data)
            if len(cluster_data["Person"]) > 0 and len(cluster_data["Flag"]) > 0:
                # print("##### ##### BISA PAIR!!")
                for flag_idx in cluster_data["Flag"]:
                    for person_idx in cluster_data["Person"]:
                        # print(">>>> cluster_data[Person]:", cluster_data["Person"])
                        if person_idx not in self.flag_pair_candidates[flag_idx]["id"]:
                            self.flag_pair_candidates[flag_idx]["id"].append(person_idx)
                            dist_idx = str(flag_idx) + "-" + str(person_idx)
                            self.flag_pair_candidates[flag_idx]["dist"].append(self.saved_dist[dist_idx])
            # else:
            #     print(">>>>>>>>>>>>>>>>>>>>>>>> Lewatii ....")

    def pair_selection(self):
        for flag_idx, pair_data in self.flag_pair_candidates.items():
            # print("$$$$$$ pairDATA:", pair_data["dist"], pair_data["id"])
            if len(pair_data["id"]) > 0:
                selected_idx = pair_data["dist"].index(min(pair_data["dist"]))
                selected_person_idx = pair_data["id"][selected_idx]
                # print("%%%%%%% flag_idx - Hasil IDX, PERSON_IDX  :", flag_idx, selected_idx, selected_person_idx)

                # get MB-Box
                # print(" !!!!!!!!!!!!!!!!!!!! self.class_det = ", self.class_det)
                # print("%%%%%%% self.person_xyxys[selected_person_idx][0], self.flag_xyxys[flag_idx][0]  :",
                # print("%%%%%%% self.person_xyxys[selected_person_idx][1], self.flag_xyxys[flag_idx][1]  :",
                #       self.person_xyxys[selected_person_idx][0], self.flag_xyxys[flag_idx][0])
                # mbbox_xyxy = get_mbbox(self.person_xyxys[selected_person_idx][1], self.flag_xyxys[flag_idx][1])

                person_xyxy = get_det_xyxy(self.det[selected_person_idx])
                flag_xyxy = get_det_xyxy(self.det[flag_idx])
                mbbox_xyxy = get_mbbox(person_xyxy, flag_xyxy)

                self.detected_mbbox.append(mbbox_xyxy)
                plot_one_box(mbbox_xyxy, self.mbbox_img, label="Person-W-Flag", color=self.rgb_mbbox)
                # if self.opt.output_txt:
                #     save_txt(self.save_path, self.opt.txt_format, mbbox_xyxy)

    def __is_eligible(self):
        if "Person" not in self.class_det or "Flag" not in self.class_det:
            # print(" ## >>>> Person or Flag NOT FOUND ")
            return False
        else:
            # print(" ## >>>> Person or Flag adaaaa donkkk ")
            return True

    def map_to_clusters(self):
        for person_idx in self.class_det["Person"]:
            # print(" *************** person_idx = ", person_idx)
            person_xyxy = get_det_xyxy(self.det[person_idx])
            # person_centroid = get_centroid_xy(person_xyxy)
            person_centroid = np_xyxy2centroid(person_xyxy)
            # self.person_xyxys.append([person_idx, person_xyxy, centroid])
            self.person_xyxys[person_idx] = [person_idx, person_xyxy, person_centroid]
            # print(">>>> centroid PersonID-%d: " % person_idx, person_centroid)
            self.find_cluster(person_centroid, "Person", person_idx)

        for flag_idx in self.class_det["Flag"]:
            # print(" *************** flag_idx = ", flag_idx)
            flag_xyxy = get_det_xyxy(self.det[flag_idx])
            # flag_centroid = get_centroid_xy(flag_xyxy)
            flag_centroid = np_xyxy2centroid(flag_xyxy)
            # self.flag_xyxys.append([flag_idx, flag_xyxy, centroid])
            self.flag_xyxys[flag_idx] = [flag_idx, flag_xyxy, flag_centroid]

            self.save_distance(flag_idx, flag_centroid)
            self.flag_pair_candidates[flag_idx] = {"id": [], "dist": []}

            # print(">>>> centroid FlagID-%d: " % flag_idx, flag_centroid)
            self.find_cluster(flag_centroid, "Flag", flag_idx)

    def save_distance(self, flag_idx, centroid):
        i = 0
        for person_idx, person_data in self.person_xyxys.items():
            # print("......... self.person_xyxys[2] = ", self.person_xyxys[2])
            # print("@@@ DATA: centroid_flag", centroid, person_idx, person_data)
            distance = get_xyxy_distance(centroid, person_data[2])
            # distance = get_xyxy_distance_manhattan(centroid, person_data[2])
            dist_idx = str(flag_idx) + "-" + str(person_idx)
            self.saved_dist[dist_idx] = distance
            i += 1

        # for i in range(len(self.person_xyxys)):
            # person_idx = self.person_xyxys[i][0]
            # distance = get_xyxy_distance(centroid, self.person_xyxys[i][2])
            # dist_idx = str(flag_idx) + "-" + str(person_idx)
            # self.saved_dist[dist_idx] = distance

    def find_cluster(self, centroid, cls, obj_idx):
        for i in range (len(self.region_xyxy)):
            reg_xyxy = self.region_xyxy[i][0]
            selected_regions = self.region_xyxy[i][1]
            if find_point(reg_xyxy, centroid):
                # print(">>>> #### This Centroid is IN THIS region-%d: " % (i+1), reg_xyxy)
                self.map(selected_regions, cls, obj_idx)
            # else:
            #     print(">>> $$$$ Wah mbuh Centroid ora nak KENEEEEE", reg_xyxy)
        # print(" >>>> WAH GAK NEMU BLASSSSS")

    def map(self, selected_regions, cls, obj_idx):
        for cluster_idx in selected_regions:
            # print(cluster_idx, cls, obj_idx, "#### $$$ Mapped into Region:", self.clusters[cluster_idx])
            # data = cls + "-" + str(obj_idx)
            # print(">>>> data: ", data)
            # self.mapped_obj[cluster_idx].append(data)
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
        # for i in range(len(self.det)):
        #     print("**** data objects = ", self.det[i])

        idx_detected = 0
        for *xyxy, conf, cls in self.det:
            # label = '%s %.2f' % (self.names[int(cls)], conf)
            # print("^^^^ data = ", self.names[int(cls)])
            # print("^^^^ TYPE data = ", type(self.names[int(cls)]))
            # self.class_det[self.names[int(cls)]] = idx_detected
            self.class_det[self.names[int(cls)]].append(idx_detected)

            idx_detected += 1

            # # print(">>>>>>>>>>>>> PLOT BBOX aja self.save_img = ", self.save_img)
            # if self.save_img or self.view_img:  # Add bbox to image
            #     label = '%s %.2f' % (self.names[int(cls)], conf)
            #     plot_one_box(xyxy, im0, label=label + "-IDX=" + str(idx_detected - 1), color=self.colors[int(cls)])

        # for c in self.det[:, -1].unique():
        #     self.class_det[self.names[int(c)]] = [i for i in range(len(self.det)) if self.det[i][-1] == c]
