from detection.algorithm.soa.yolo_v3.components.utils.datasets import *
from detection.algorithm.soa.yolo_v3.components.utils.utils import *
# from detection.algorithm.soa.yolo_v3.etc.commons.opencv_helpers import *
from ext_lib.commons.opencv_helpers import *
from detection.algorithm.soa.yolo_v3.components.utils.utils import get_current_time
from detection.algorithm.soa.yolo_v3.etc.commons.yolo_functions import YOLOFunctions
import logging
import json
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class YOLOv3(YOLOFunctions):
    def __init__(self, conf):
        L.log(LOG_NOTICE, "Reformatting configuration data")
        conf = self._reformat_conf(conf)
        L.log(LOG_NOTICE, json.dumps(conf))
        super().__init__(conf)
        self.conf = conf
        L.log(LOG_NOTICE, "Initializing Configuration")
        self.__initialize_configurations()
        L.log(LOG_NOTICE, "Configuration initialized")

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
        L.log(LOG_NOTICE, "[%s] Initialize YOLO Configuration" % get_current_time())
        t0_load_weight = time.time()
        self._load_weight()
        t_load_weight = time.time() - t0_load_weight
        # print(".. Load `weight` in (%.3fs)" % t_load_weight)

        # Latency: Load YOLOv3 Weight
        L.log(LOG_NOTICE, 'Latency [Load `weight`]: (%.5fs)' % t_load_weight)

        t0_load_eval = time.time()
        self._eval_model()
        t_load_eval_model = time.time() - t0_load_eval
        # print(".. Load function `eval_model` in (%.3fs)" % t_load_eval_model)

        # Latency: Execute Evaluation Model
        L.log(LOG_NOTICE, 'Latency [Load `Eval Model`]: (%.5fs)' % t_load_eval_model)

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
        L.log(LOG_NOTICE, '[%s] Pre-processing time (%.3f ms)' % (get_current_time(), t1_preproc))
        # TODO: To capture the latency of the PRE-Processing

        return image4yolo

    def get_detection_results(self, img, original_frame, is_yolo_format=True):
        padded_img = img
        if not is_yolo_format:
            padded_img = self.__img2yoloimg(img)

        # Get detections
        pred = None
        t0_det = time.time()

        t0_from_numpy = time.time()
        img_torch = torch.from_numpy(padded_img)
        tdiff_from_numpy = (time.time() - t0_from_numpy) * 1000  # to ms

        t0_image4yolo = time.time()
        image4yolo = img_torch.to(self.device)
        tdiff_image4yolo = (time.time() - t0_image4yolo) * 1000  # to ms

        t0_pred = time.time()
        if image4yolo.ndimension() == 3:
            image4yolo = image4yolo.unsqueeze(0)
        try:
            pred = self.model(image4yolo)[0]
        except Exception as e:
            L.error("[ERROR][get_detection_results]: %s" % str(e))
        tdiff_pred = (time.time() - t0_pred) * 1000  # to ms

        tdiff_inference = (time.time() - t0_det) * 1000  # to ms

        # Latency: Inference
        L.log(LOG_NOTICE, '[%s] Inference time (%.3f ms)' % (get_current_time(), tdiff_inference))

        L.log(LOG_NOTICE, '[%s] Function (from_numpy) time (%.3f ms)' % (get_current_time(), tdiff_from_numpy))
        L.log(LOG_NOTICE, '[%s] Function (image4yolo) time (%.3f ms)' % (get_current_time(), tdiff_image4yolo))
        L.log(LOG_NOTICE, '[%s] Prediction time (%.3f ms)' % (get_current_time(), tdiff_pred))

        # Default: Disabled
        # if self.conf["half"]:
        #     pred = pred.float()

        # Apply NMS: Non-Maximum Suppression
        t0_nms = time.time()
        # to Removes detections with lower object confidence score than 'conf_thres'
        pred = non_max_suppression(pred, self.conf["conf_thres"], self.conf["iou_thres"],
                                   classes=None,
                                   agnostic=self.conf["agnostic_nms"])
        tdiff_nms = ((time.time() - t0_nms) * 1000)
        L.log(LOG_NOTICE, '# Total Non-Maximum Suppression (NMS) time: (%.3f ms)' % tdiff_nms)

        # Get detection
        t0_get_detection = time.time()
        bbox_data = []
        det = None
        if len(pred) == 1 and pred[0] is None:
            # DO NOTHING
            pass
        else:
            for i, det in enumerate(pred):  # detections per image
                if det is not None and len(det):  # run ONCE
                    # Rescale boxes from img_size to raw_img size
                    det[:, :4] = scale_coords(image4yolo.shape[2:], det[:, :4], original_frame.shape).round()

                    # Extracts detection results
                    bbox_data = self._extract_detection_results(det)
                    break

        t1_get_detection = ((time.time() - t0_get_detection) * 1000)
        L.log(LOG_NOTICE, '# Get Detection time: (%.3f ms)' % t1_get_detection)
        # TODO: To capture the latency of the POST-Processing

        names = load_classes(self.conf["names"])

        return bbox_data, det, names, (tdiff_inference + tdiff_nms), tdiff_from_numpy, tdiff_image4yolo, tdiff_pred

        # return pred
        # Apply Classifier: Default DISABLED
        # if self.classify:
        #     self.pred = apply_classifier(self.pred, self.modelc, image4yolo, raw_img)

    # def _extract_detection_results(self, det, raw_img, this_frame_id):
    def _extract_detection_results(self, det):
        # print("@@@@ _extract_detection_results....")
        """ A function to do optional actions: Save cropped file, bbox in txt, bbox images """

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
