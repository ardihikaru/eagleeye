from pcs.candidate_selection.cs_v2.region_cluster import RegionCluster
from ext_lib.commons.util import find_point
from ext_lib.commons.opencv_helpers import get_det_xyxy, np_xyxy2xywh, get_mbbox, np_xyxy2centroid, get_xyxy_distance_manhattan, get_xyxy_distance, save_txt
import asab
import simplejson as json


class CSv2(RegionCluster):
    def __init__(self):
        super().__init__()
        self.height, self.width, self.channels = None, None, None
        self.det = None  # Original detected objects
        self.class_det = {"Person": [], "Flag": []}
        self.names = None
        self.detected_mbbox = []
        self.pih_label = asab.Config["bbox_config"]["pih_label"]
        self.rgb_mbbox = json.loads(asab.Config["bbox_config"]["pih_color"])
        self.smoothen_pih = bool(int(asab.Config["objdet:yolo"]["smoothen_pih"]))

        self.paired_flags = {}
        self.saved_dist = {}  # of (FlagID, PersonID), e.g. ["0-0"] = 80

        self.person_xyxys = {}
        self.flag_xyxys = {}
        self.flag_pair_candidates = {}
        self.selected_pairs = []
        self._prev_pairs = None
        # self.bbox_data = []  # an optional, since we can use `det`

    def initialize(self, det, names, h, w, c, prev_pairs):
        # self.bbox_data = bbox_data
        self._prev_pairs = prev_pairs
        self.det = det
        self.names = names
        self.height = h
        self.width = w
        self.channels = c

        # Reset on every call
        self.class_det = {"Person": [], "Flag": []}
        self.paired_flags = {}
        self.saved_dist = {}  # of (FlagID, PersonID), e.g. ["0-0"] = 80
        self.person_xyxys = {}
        self.flag_xyxys = {}
        self.flag_pair_candidates = {}
        self.selected_pairs = []
        self.detected_mbbox = []
        self._set_empty_object_data()

    def run(self):
        self.__extract()

        if self.__is_eligible():
            self.map_to_clusters()
            self.find_pair_candidates()
            self.pair_selection()

            # if no mbbox found so far, try to compare with previous pair Person and Flag objects
            # TODO: to use previous data to fix missing mbbox object due to bad training dataset

    def __is_flag_valid(self, flag_idx, person_idx):
        person_xyxy = get_det_xyxy(self.det[person_idx])
        flag_xyxy = get_det_xyxy(self.det[flag_idx])

        person_xywh = np_xyxy2xywh(person_xyxy)
        flag_xywh = np_xyxy2xywh(flag_xyxy)
        if flag_xywh[3] > person_xywh[3]:
            return False
        return True

    def __is_distance_valid(self, dist_idx):
        dist_th = 450.0
        if self.saved_dist[dist_idx] < dist_th:
            return True
        return False

    # this function aims to delete stored pair with higher distant
    # return True if new pair is having shorter distant
    def _validate_and_delete_higher_distant_pair(self, ignored_flag_id, current_person_idx, current_dist_idx):
        is_validated = True
        current_distant = self.saved_dist[current_dist_idx]
        for flag_id, pair_data in self.flag_pair_candidates.items():
            if flag_id != ignored_flag_id and current_person_idx in pair_data["id"]:
                # locate the index of stored person_id, and get its distant
                for i in range(len(pair_data["id"])):
                    # if current distant is smaller, then, delete the stored pair data: in key `id` and `dist`
                    if pair_data["id"][i] == current_person_idx:
                        if current_distant < pair_data["dist"][i]:
                            del pair_data["id"][i]
                            del pair_data["dist"][i]
                            break  # exit loop once terget data has been deleted
                        else:
                            is_validated = False
                            break  # exit loop once terget data has been deleted
        return is_validated

    def find_pair_candidates(self):
        for cluster_data in self.mapped_obj:
            if len(cluster_data["Person"]) > 0 and len(cluster_data["Flag"]) > 0:
                for flag_idx in cluster_data["Flag"]:
                    for person_idx in cluster_data["Person"]:
                        dist_idx = str(flag_idx) + "-" + str(person_idx)

                        if self.__is_flag_valid(flag_idx, person_idx) and self.__is_distance_valid(dist_idx):
                            if person_idx not in self.flag_pair_candidates[flag_idx]["id"]:
                                if self.smoothen_pih:
                                    # also, check if similar PiH candidate has been stored before
                                    if self._validate_and_delete_higher_distant_pair(flag_idx, person_idx, dist_idx):
                                        self.flag_pair_candidates[flag_idx]["id"].append(person_idx)
                                        self.flag_pair_candidates[flag_idx]["dist"].append(self.saved_dist[dist_idx])
                                else:
                                    self.flag_pair_candidates[flag_idx]["id"].append(person_idx)
                                    self.flag_pair_candidates[flag_idx]["dist"].append(self.saved_dist[dist_idx])

    def pair_selection(self):
        for flag_idx, pair_data in self.flag_pair_candidates.items():
            # if multiple `person_idx` are found in a single flag, then, choose one with closest distance
            if len(pair_data["id"]) > 0:
                selected_idx = pair_data["dist"].index(min(pair_data["dist"]))
                selected_person_idx = pair_data["id"][selected_idx]

                person_xyxy = get_det_xyxy(self.det[selected_person_idx])
                flag_xyxy = get_det_xyxy(self.det[flag_idx])
                mbbox_xyxy = get_mbbox(person_xyxy, flag_xyxy)

                # save selected pairs
                self.selected_pairs.append({
                    "Person": person_xyxy,
                    "Flag": flag_xyxy
                })

                # Bugfix: format numpy-float into float data type
                for i in range(len(mbbox_xyxy)):
                    mbbox_xyxy[i] = float(mbbox_xyxy[i])

                self.detected_mbbox.append(mbbox_xyxy)
                # plot_one_box(mbbox_xyxy, self.mbbox_img, label=self.pih_label, color=self.rgb_mbbox)

    def __is_eligible(self):
        # if "Person" not in self.class_det or "Flag" not in self.class_det:
        if len(self.class_det["Person"]) == 0 or len(self.class_det["Flag"]) == 0:
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
        for i in range(len(self.region_xyxy)):
            reg_xyxy = self.region_xyxy[i][0]
            selected_regions = self.region_xyxy[i][1]
            if find_point(reg_xyxy, centroid):
                self.map(selected_regions, cls, obj_idx)

    def map(self, selected_regions, cls, obj_idx):
        for cluster_idx in selected_regions:
            self.mapped_obj[cluster_idx][cls].append(obj_idx)

    def get_detected_mbbox(self):
        return self.detected_mbbox

    def get_selected_pairs(self):
        return self.selected_pairs

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
