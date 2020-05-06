# Persistence Module v1
# 	Compiled:	05 May 2020

# Sliding Window implementation: https://github.com/imravishar/sliding_window
from window_slider import Slider
import numpy as np
from libs.settings import common_settings

# self.persistence_window = 45 # 1.5s for a 30FPS video
# self.tolerance_limit = 15 # 0.5s for a 30FPS video


class PersistenceDetection:
    def __init__(self, opt, cur_frame_id, total_pih_candidates, period_pih_candidates):
        super().__init__()
        self.opt = opt
        self.total_pih_candidates = total_pih_candidates
        self.period_pih_candidates = period_pih_candidates
        self.cur_frame_id = cur_frame_id
        self.persistence_window = common_settings["persistence_detection"]["persistence_window"]
        self.tolerance_limit = self.__get_tolerance_limit()
        self.pih_label_cand = common_settings["bbox_config"]["pih_label_cand"]
        self.pih_label = common_settings["bbox_config"]["pih_label"]
        self.selected_label = self.pih_label_cand  # Default
        print("[PERSISTENCE WINDOW=%d and TOLERANCE LIMIT=%d]"
              % (self.persistence_window, self.tolerance_limit))

    def __get_tolerance_limit(self):
        tolerance_percentage = common_settings["persistence_detection"]["tolerance_limit_percentage"]
        tolerance_limit = int(self.persistence_window * tolerance_percentage)
        return tolerance_limit

    def get_persistence_window(self):
        return self.persistence_window

    def run(self):
        if self.total_pih_candidates >= self.persistence_window:
            self.persistence_module_window()
        else:
            self.selected_label = self.pih_label

    # Get last N frames; N = self.persistence_window
    def get_persistence_batch(self):
        check_batch = np.asarray(self.period_pih_candidates)
        return check_batch

    # Check for persistence of a batch
    def persistence_module(self, check_batch):
        persistence_count = 0
        tolerance_count = 0

        while persistence_count < self.persistence_window - 1:
            current_frame_id = check_batch[persistence_count]
            next_frame_id = check_batch[persistence_count + 1]

            # Check next frame to see whether 'Flag' object is still detected
            if (current_frame_id + 1) != next_frame_id:
                tolerance_count += 1

            persistence_count += 1

        persistence_count += 1  # Since the first frameID contributes to a count

        if tolerance_count <= self.tolerance_limit:
            self.selected_label = self.pih_label
            print("[DBG]\tPiH Detected! Set current frameID=%s Label as --> %s" % (str(self.cur_frame_id), self.pih_label))

            print("[DBG]\tpersistence_count=%d; tolerance_count=%d" % (persistence_count, tolerance_count))
        else:
            print("[DBG]\tPiH not detected! Set current frameID=%s Label as --> %s" % (str(self.cur_frame_id), self.pih_label_cand))
            print("[DBG]\tpersistence_count=%d; tolerance_count=%d" % (persistence_count, tolerance_count))

    def get_label(self):
        return self.selected_label

    # Sliding window implementation of persistence_module
    def persistence_module_window(self):
        # Get check_batch
        check_batch = self.get_persistence_batch()

        # window_slider parameter
        bucket_size = self.persistence_window
        overlap_count = self.persistence_window - self.tolerance_limit

        # Sliding Window
        slider = Slider(bucket_size, overlap_count)
        slider.fit(check_batch)

        while True:
            window_data = slider.slide()

            # Stop if the window_data does not have enough data
            if window_data.shape[0] < self.persistence_window:
                break

            print("[DBG]\twindow_data: %s" % str(window_data))
            self.persistence_module(window_data)

            if slider.reached_end_of_list():
                break
