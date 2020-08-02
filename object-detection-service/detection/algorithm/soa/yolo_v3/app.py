from detection.algorithm.soa.yolo_v3.components.utils.datasets import *
from detection.algorithm.soa.yolo_v3.components.utils.utils import *
from detection.algorithm.soa.yolo_v3.etc.commons.opencv_helpers import *
from detection.algorithm.soa.yolo_v3.components.utils.utils import get_current_time
from detection.algorithm.soa.yolo_v3.etc.commons.yolo_functions import YOLOFunctions


class YOLOv3(YOLOFunctions):
    def __init__(self, conf):
        conf = self._reformat_conf(conf)
        super().__init__(conf)
        self.conf = conf
        self.__initialize_configurations()

        # Set related parameters
        self.total_proc_frames = 0

    def _reformat_conf(self, conf_section):
        conf = dict(conf_section)
        conf["agnostic_nms"] = bool(int(conf["agnostic_nms"]))
        conf["half"] = bool(int(conf["half"]))
        conf["save_txt"] = bool(int(conf["save_txt"]))
        conf["dump_raw_img"] = bool(int(conf["dump_raw_img"]))
        conf["dump_bbox_img"] = bool(int(conf["dump_bbox_img"]))
        conf["dump_crop_img"] = bool(int(conf["dump_crop_img"]))
        conf["auto_restart"] = bool(int(conf["auto_restart"]))
        conf["cv_out"] = bool(int(conf["cv_out"]))

        # conf["candidate_selection"] = bool(int(conf["candidate_selection"]))
        # conf["Persistence_validation"] = bool(int(conf["Persistence_validation"]))

        conf["img_size"] = int(conf["img_size"])
        conf["window_size_height"] = int(conf["window_size_height"])
        conf["window_size_width"] = int(conf["window_size_width"])

        conf["conf_thres"] = float(conf["conf_thres"])
        conf["iou_thres"] = float(conf["window_size_width"])
        return conf

    def __initialize_configurations(self):
        print("\n[%s] Initialize YOLO Configuration" % get_current_time())
        t0_load_weight = time.time()
        self._load_weight()
        t_load_weight = time.time() - t0_load_weight
        print(".. Load `weight` in (%.3fs)" % t_load_weight)

        # Latency: Load YOLOv3 Weight
        print('Latency [Load `weight`]: (%.5fs)' % t_load_weight)

        t0_load_eval = time.time()
        self._eval_model()
        t_load_eval_model = time.time() - t0_load_eval
        print(".. Load function `eval_model` in (%.3fs)" % t_load_eval_model)

        # Latency: Execute Evaluation Model
        print('Latency [Load `Eval Model`]: (%.5fs)' % t_load_eval_model)

        self._get_names_colors()

    def __img2yoloimg(self, image):
        t0_preproc = time.time()
        # Padded resize
        image4yolo = letterbox(image, new_shape=self.img_size)[0]

        # Convert
        image4yolo = image4yolo[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        image4yolo = np.ascontiguousarray(image4yolo,
                                          dtype=np.float16 if self.conf["half"] else np.float32)  # uint8 to fp16/fp32
        image4yolo /= 255.0  # 0 - 255 to 0.0 - 1.0
        t1_preproc = (time.time() - t0_preproc) * 1000  # to ms
        print('[%s] Pre-processing time (%.3f ms)' % (get_current_time(), t1_preproc))
        # TODO: To capture the latency of the PRE-Processing

        return image4yolo

    def get_detection_results(self, img, is_yolo_format=True):
        padded_img = img
        if not is_yolo_format:
            padded_img = self.__img2yoloimg(img)

        # Get detections
        pred = None
        t0_det = time.time()
        img_torch = torch.from_numpy(padded_img)
        image4yolo = img_torch.to(self.device)
        if image4yolo.ndimension() == 3:
            image4yolo = image4yolo.unsqueeze(0)
        try:
            pred = self.model(image4yolo)[0]
        except Exception as e:
            print("~~ EEROR: ", e)
        t1_inference = (time.time() - t0_det) * 1000  # to ms

        # Latency: Inference
        print('[%s] Inference time (%.3f ms)' % (get_current_time(), t1_inference))

        # Default: Disabled
        # if self.conf["half"]:
        #     pred = pred.float()

        # Apply NMS: Non-Maximum Suppression
        ts_nms = time.time()
        # to Removes detections with lower object confidence score than 'conf_thres'
        pred = non_max_suppression(pred, self.conf["conf_thres"], self.conf["iou_thres"],
                                   classes=None,
                                   agnostic=self.conf["agnostic_nms"])
        t1_nms = ((time.time() - ts_nms) * 1000)
        print('\n # Total Non-Maximum Suppression (NMS) time: (%.3f ms)' % t1_nms)

        # Get detection
        t0_get_detection = time.time()
        bbox_data = None
        det = None
        for i, det in enumerate(pred):  # detections per image
            if det is not None and len(det):  # run ONCE
                # Rescale boxes from img_size to raw_img size
                det[:, :4] = scale_coords(image4yolo.shape[2:], det[:, :4], img.shape).round()

                # Extracts detection results
                bbox_data = self._extract_detection_results(det)
                # print(" >>>>> bbox_data =", bbox_data)
                break
        t1_get_detection = ((time.time() - t0_get_detection) * 1000)
        print('\n # Get Detection time: (%.3f ms)' % t1_get_detection)
        # TODO: To capture the latency of the POST-Processing

        names = load_classes(self.conf["names"])

        return bbox_data, det, names
        # return pred
        # Apply Classifier: Default DISABLED
        # if self.classify:
        #     self.pred = apply_classifier(self.pred, self.modelc, image4yolo, raw_img)

    # def _extract_detection_results(self, det, raw_img, this_frame_id):
    def _extract_detection_results(self, det):
        print("@@@@ _extract_detection_results....")
        """ A function to do optional actions: Save cropped file, bbox in txt, bbox images """
        # t0_copy_image = time.time()
        # original_img = raw_img.copy()
        # t1_copy_image = (time.time() - t0_copy_image) * 1000  # to ms
        # print('[%s] Latency of copying image data of frame-%s (%.3f ms)' % (get_current_time(), str(this_frame_id),
        #                                                                     t1_copy_image))

        # TODO: We can do the parallel computation to enhance the performance further!
        # Draw BBox information into images
        idx_detected = 0
        bbox_data = []
        for *xyxy, conf, cls in det:
            numpy_xyxy = get_det_xyxy(xyxy)
            this_label = '%s %.2f' % (self.names[int(cls)], conf)
            this_color = self.colors[int(cls)]
            idx_detected += 1

            # Save cropped files
            # self._save_cropped_img(xyxy, raw_img, idx_detected, self.names[int(cls)], this_frame_id,
            #                        self.conf["file_ext"])
            # Save bbox information
            # self._safety_store_txt(xyxy, this_frame_id, self.names[int(cls)], str(round(float(conf), 2)))

            this_bbox = {
                "obj_idx": idx_detected,
                "xyxy": [str(val) for val in numpy_xyxy],
                "label": this_label,
                "color": [str(color) for color in this_color]
            }
            bbox_data.append(this_bbox)
            # plot_one_box(xyxy, raw_img, label=this_label, color=this_color)
        return bbox_data
        # Save BBox image
        # self._save_results(raw_img, this_frame_id)

    # def test_print_bbox(self, pred):
    #     print(" @@@ test_print_bbox ...")
    #     # Process detections
    #     '''
    #     p = path
    #     s = string for printing
    #     im0 = image (matrix)
    #     '''
    #
    #     try:
    #         for i, det in enumerate(pred):  # detections per image
    #             print(" ######### i & det:", i, det)
    #             # if det is not None and len(det):
    #             # Rescale boxes from img_size to im0 size
    #             # det[:, :4] = scale_coords(image4yolo.shape[2:], det[:, :4], raw_img.shape).round()
    #
    #             # Export results: Raw image OR BBox image OR Crop image OR BBox txt
    #             # if self.opt.dump_raw_img or self.opt.dump_bbox_img or self.opt.dump_crop_img or self.opt.save_txt:
    #             # if self.conf["cv_out"]:
    #             #     self._manage_detection_results(det, raw_img, this_frame_id)
    #
    #     except Exception as e:
    #         print("ERROR Plotting: ", e)

    #
    # def detect(self, raw_img, frame_id):
    #     print("\n[%s] Starting YOLOv3 for frame-%s" % (get_current_time(), frame_id))
    #
    #     # DO THE DETECTION HERE!
    #     self._save_results(raw_img, frame_id, is_raw=True)
    #
    #     # Padded resize
    #     image4yolo = letterbox(raw_img, new_shape=self.img_size)[0]
    #
    #     # Convert
    #     image4yolo = image4yolo[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    #     image4yolo = np.ascontiguousarray(image4yolo, dtype=np.float16 if self.half else np.float32)  # uint8 to fp16/fp32
    #     image4yolo /= 255.0  # 0 - 255 to 0.0 - 1.0
    #
    #     # Start processing image
    #     print("[%s] Received frame-%d" % (get_current_time(), int(frame_id)))
    #     self._process_detection(image4yolo, raw_img, frame_id)
    #
    # def _process_detection(self, image4yolo, raw_img, this_frame_id):
    #
    #     # Get detections
    #     ts_det = time.time()
    #     img_torch = torch.from_numpy(image4yolo) #.to(self.device)
    #     image4yolo = img_torch.to(self.device)
    #     if image4yolo.ndimension() == 3:
    #         image4yolo = image4yolo.unsqueeze(0)
    #     try:
    #         self.pred = self.model(image4yolo)[0]
    #     except Exception as e:
    #         print("~~ EEROR: ", e)
    #     t_inference = (time.time() - ts_det) * 1000  # to ms
    #
    #     # Latency: Inference
    #     print('[%s] DONE Inference of frame-%s (%.3f ms)' % (get_current_time(), str(this_frame_id), t_inference))
    #
    #     # Default: Disabled
    #     if self.conf["half"]:
    #         self.pred = self.pred.float()
    #
    #     # Apply NMS: Non-Maximum Suppression
    #     # ts_nms = time.time()
    #     # to Removes detections with lower object confidence score than 'conf_thres'
    #     self.pred = non_max_suppression(self.pred, self.conf["conf_thres"], self.conf["iou_thres"],
    #                                     classes=self.conf["classes"],
    #                                     agnostic=self.conf["agnostic_nms"])
    #     # print('\n # Total Non-Maximum Suppression (NMS) time: (%.3fs)' % (time.time() - ts_nms))
    #
    #     # Apply Classifier: Default DISABLED
    #     if self.classify:
    #         self.pred = apply_classifier(self.pred, self.modelc, image4yolo, raw_img)
    #
    #     # Process detections
    #     '''
    #     p = path
    #     s = string for printing
    #     im0 = image (matrix)
    #     '''
    #
    #     try:
    #         for i, det in enumerate(self.pred):  # detections per image
    #             if det is not None and len(det):
    #                 # Rescale boxes from img_size to im0 size
    #                 det[:, :4] = scale_coords(image4yolo.shape[2:], det[:, :4], raw_img.shape).round()
    #
    #                 # Export results: Raw image OR BBox image OR Crop image OR BBox txt
    #                 # if self.opt.dump_raw_img or self.opt.dump_bbox_img or self.opt.dump_crop_img or self.opt.save_txt:
    #                 if self.conf["cv_out"]:
    #                     self._manage_detection_results(det, raw_img, this_frame_id)
    #
    #     except Exception as e:
    #         print("ERROR Plotting: ", e)
