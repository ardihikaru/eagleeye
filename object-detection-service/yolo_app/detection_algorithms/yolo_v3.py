from yolo_app.components.models import *  # set ONNX_EXPORT in models.py
from yolo_app.components.utils.datasets import *
from yolo_app.components.utils.utils import *
from yolo_app.etc.commons.opencv_helpers import *
from yolo_app.components.utils.utils import get_current_time
from yolo_app.etc.commons.yolo_functions import YOLOFunctions


class YOLOv3(YOLOFunctions):
    def __init__(self, opt):
        super().__init__(opt)
        self.opt = opt
        self.classify = False
        self.total_proc_frames = 0

        self.vid_path, self.vid_writer = None, None

        # (320, 192) or (416, 256) or (608, 352) for (height, width)
        self.img_size = (320, 192) if ONNX_EXPORT else opt.img_size

        self.out, self.source, self.weights, self.half, self.view_img, self.save_txt = opt.output, opt.source, opt.weights, opt.half, opt.view_img, opt.save_txt
        self.webcam = self.source == '0' or self.source.startswith('rtsp') or self.source.startswith('http') or self.source.endswith('.txt')

        # Initialize model
        self.model = Darknet(opt.cfg, self.img_size)
        self.mbbox = None # Merge Bounding Box

        # Initialize device configuration
        self.device = torch_utils.select_device(device='cpu' if ONNX_EXPORT else opt.device)

        self.__initialize_configurations()

    def __initialize_configurations(self):
        print("\n[%s] Initialize YOLO Configuration" % get_current_time())
        t0_load_weight = time.time()
        self.__load_weight()
        t_load_weight = time.time() - t0_load_weight
        print(".. Load `weight` in (%.3fs)" % t_load_weight)

        # Latency: Load YOLOv3 Weight
        print('Latency [Load `weight`]: (%.5fs)' % t_load_weight)

        t0_load_eval = time.time()
        self.__eval_model()
        t_load_eval_model = time.time() - t0_load_eval
        print(".. Load function `eval_model` in (%.3fs)" % t_load_eval_model)

        # Latency: Execute Evaluation Model
        print('Latency [Load `Eval Model`]: (%.5fs)' % t_load_eval_model)

        self.__get_names_colors()

    def detect(self, raw_img, frame_id):
        print("\n[%s] Starting YOLOv3 for frame-%s" % (get_current_time(), frame_id))

        # DO THE DETECTION HERE!
        self._save_results(raw_img, frame_id, is_raw=True)

        # Padded resize
        image4yolo = letterbox(raw_img, new_shape=self.img_size)[0]

        # Convert
        image4yolo = image4yolo[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        image4yolo = np.ascontiguousarray(image4yolo, dtype=np.float16 if self.half else np.float32)  # uint8 to fp16/fp32
        image4yolo /= 255.0  # 0 - 255 to 0.0 - 1.0

        # Start processing image
        print("[%s] Received frame-%d" % (get_current_time(), int(frame_id)))
        self._process_detection(image4yolo, raw_img, frame_id)

    def _process_detection(self, image4yolo, raw_img, this_frame_id):

        # Get detections
        ts_det = time.time()
        img_torch = torch.from_numpy(image4yolo) #.to(self.device)
        image4yolo = img_torch.to(self.device)
        if image4yolo.ndimension() == 3:
            image4yolo = image4yolo.unsqueeze(0)
        try:
            self.pred = self.model(image4yolo)[0]
        except Exception as e:
            print("~~ EEROR: ", e)
        t_inference = (time.time() - ts_det) * 1000  # to ms

        # Latency: Inference
        print('[%s] DONE Inference of frame-%s (%.3f ms)' % (get_current_time(), str(this_frame_id), t_inference))

        # Default: Disabled
        if self.opt.half:
            self.pred = self.pred.float()

        # Apply NMS: Non-Maximum Suppression
        # ts_nms = time.time()
        # to Removes detections with lower object confidence score than 'conf_thres'
        self.pred = non_max_suppression(self.pred, self.opt.conf_thres, self.opt.iou_thres,
                                        classes=self.opt.classes,
                                        agnostic=self.opt.agnostic_nms)
        # print('\n # Total Non-Maximum Suppression (NMS) time: (%.3fs)' % (time.time() - ts_nms))

        # Apply Classifier: Default DISABLED
        if self.classify:
            self.pred = apply_classifier(self.pred, self.modelc, image4yolo, raw_img)

        # Process detections
        '''
        p = path
        s = string for printing
        im0 = image (matrix)
        '''

        try:
            for i, det in enumerate(self.pred):  # detections per image
                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(image4yolo.shape[2:], det[:, :4], raw_img.shape).round()

                    # Export results: Raw image OR BBox image OR Crop image OR BBox txt
                    # if self.opt.dump_raw_img or self.opt.dump_bbox_img or self.opt.dump_crop_img or self.opt.save_txt:
                    if self.opt.cv_out:
                        self._manage_detection_results(det, raw_img, this_frame_id)

        except Exception as e:
            print("ERROR Plotting: ", e)

    def _manage_detection_results(self, det, raw_img, this_frame_id):
        """
            A function to do optional actions: Save cropped file, bbox in txt, bbox images
        """
        t0_copy_image = time.time()
        original_img = raw_img.copy()
        t1_copy_image = (time.time() - t0_copy_image) * 1000  # to ms
        print('[%s] Latency of copying image data of frame-%s (%.3f ms)' % (get_current_time(), str(this_frame_id),
                                                                            t1_copy_image))

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
            self._save_cropped_img(xyxy, original_img, idx_detected, self.names[int(cls)], this_frame_id,
                                   self.opt.file_ext)
            # Save bbox information
            self._safety_store_txt(xyxy, this_frame_id, self.names[int(cls)], str(round(float(conf), 2)))

            this_bbox = {
                "obj_idx": idx_detected,
                "xyxy": [str(val) for val in numpy_xyxy],
                "label": this_label,
                "color": [str(color) for color in this_color]
            }
            bbox_data.append(this_bbox)
            plot_one_box(xyxy, raw_img, label=this_label, color=this_color)

        # Save BBox image
        self._save_results(raw_img, this_frame_id)

    def __load_weight(self):
        # Load weights
        attempt_download(self.weights)
        if self.weights.endswith('.pt'):  # pytorch format
            self.model.load_state_dict(torch.load(self.weights, map_location=self.device)['model'])
        else:  # darknet format
            load_darknet_weights(self.model, self.weights)

        # Fuse Conv2d + BatchNorm2d layers
        # model.fuse()

    def __second_stage_classifier(self):
        # Second-stage classifier
        if self.classify:
            self.modelc = torch_utils.load_classifier(name='resnet101', n=2)  # initialize
            self.modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=self.device)['model'])  # load weights
            self.modelc.to(self.device).eval()

    def __eval_model(self):
        # Eval mode
        self.model.to(self.device).eval()

    # Optional
    def __export_mode(self):
        # Export mode
        if ONNX_EXPORT:
            img = torch.zeros((1, 3) + self.img_size)  # (1, 3, 320, 192)
            torch.onnx.export(self.model, img, 'weights/export.onnx', verbose=False, opset_version=10)

            # Validate exported model
            import onnx
            model = onnx.load('weights/export.onnx')  # Load the ONNX model
            onnx.checker.check_model(model)  # Check that the IR is well formed
            print(onnx.helper.printable_graph(model.graph))  # Print a human readable representation of the graph
            return

    def __half_precision(self):
        # Half precision
        self.half = self.half and self.device.type != 'cpu'  # half precision only supported on CUDA
        if self.half:
            self.model.half()

    def __set_data_loader(self):
        # Set Dataloader
        self.vid_path, self.vid_writer = None, None
        if self.webcam:
            self.view_img = True
            self.save_img = True
            # self.save_img = False
            torch.backends.cudnn.benchmark = True  # set True to speed up constant image size inference
            self.dataset = LoadStreams(self.source, img_size=self.img_size, half=self.half)
        else:
            self.save_img = True
            self.dataset = LoadImages(self.source, img_size=self.img_size, half=self.half)

    def __get_names_colors(self):
        # Get names and colors
        self.names = load_classes(self.opt.names)
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]
