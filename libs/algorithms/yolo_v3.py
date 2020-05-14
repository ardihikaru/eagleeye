from sys import platform

from models import *  # set ONNX_EXPORT in models.py
from utils.datasets import *
from utils.utils import *
from libs.commons.opencv_helpers import *

from libs.algorithms.mod_v1 import MODv1
from libs.algorithms.mod_v2 import MODv2
from redis import StrictRedis
import json
from libs.settings import common_settings
from libs.addons.redis.translator import redis_set, redis_get, pub
from libs.addons.redis.utils import store_latency, store_fps
import imagezmq


class YOLOv3:
    def __init__(self, opt, frame_id=0):
        self.frame_id = frame_id
        self.fps = common_settings["drone_info"]["fps"]
        self.n_labels = 2 # This is fixed, since we desire 2 labels: Person and Flag
        self.opt = opt
        self.save_path = None
        self.t0 = None
        self.str_output = ""
        self.classify = False
        self.total_proc_frames = 0

        # (320, 192) or (416, 256) or (608, 352) for (height, width)
        self.img_size = (320, 192) if ONNX_EXPORT else opt.img_size

        self.out, self.source, self.weights, self.half, self.view_img, self.save_txt = opt.output, opt.source, opt.weights, opt.half, opt.view_img, opt.save_txt
        self.webcam = self.source == '0' or self.source.startswith('rtsp') or self.source.startswith('http') or self.source.endswith('.txt')

        # Initialize
        self.device = torch_utils.select_device(device='cpu' if ONNX_EXPORT else opt.device)
        if os.path.exists(self.out):
            shutil.rmtree(self.out)  # delete output folder
        os.makedirs(self.out)  # make new output folder
        os.makedirs(self.out+"/original")  # make enlarge folder
        os.makedirs(self.out+"/enlarge")  # make enlarge folder
        os.makedirs(self.out+"/mbbox")  # make bbox folder
        os.makedirs(self.out+"/bbox")  # make bbox folder
        os.makedirs(self.out+"/crop")  # make crop folder
        os.makedirs(self.out+"/txt")  # make txt folder

        # # Empty folders
        # mbbox_folder = opt.mbbox_output + str(opt.drone_id)
        # if os.path.exists(mbbox_folder):
        #     shutil.rmtree(mbbox_folder)  # delete output folder
        # os.makedirs(mbbox_folder)  # make new output folder

        # Initialize model
        self.model = Darknet(opt.cfg, self.img_size)
        self.mbbox = None # Merge Bounding Box
        # self.detected_mbbox = 0
        self.detected_mbbox = []

        # Sef Default Detection Algorithms
        # self.default_algorithm = opt.default_detection
        # self.mbbox_algorithm = opt.mbbox_detection

        # Set W and H enlarging ratio
        self.w_ratio = opt.w_ratio
        self.h_ratio = opt.h_ratio

        self.time_inference = 0.0
        self.time_nms = 0.0
        self.time_mbbox = 0.0
        self.time_default = 0.0
        self.time_inference_list = []
        self.time_nms_list = []
        self.time_mbbox_list = []
        self.time_default_list = []

        self.csv_inference = "time_inference_latency.csv"
        self.csv_nms = "time_nms_latency.csv"
        self.csv_mbbox = "time_mbbox_latency.csv"
        self.csv_default = "time_bbox_latency.csv"

        self.mbbox_img = None
        self.auto_restart = True
        self.manual_stop = False

        self.__set_redis()
        self.save_img = True

        open_port = self.__get_open_port(int(opt.sub_channel))
        self.image_hub = imagezmq.ImageHub(open_port=open_port, REQ_REP=False)
        # self.image_hub = imagezmq.ImageHub(open_port='tcp://127.0.0.1:5555', REQ_REP=False)

    def __get_open_port(self, channel):
        return 'tcp://127.0.0.1:555' + str(channel)

    def __set_redis(self):
        self.rc = StrictRedis(
            host=common_settings["redis_config"]["hostname"],
            port=common_settings["redis_config"]["port"],
            password=common_settings["redis_config"]["password"],
            db=common_settings["redis_config"]["db"],
            decode_responses=True
        )

        self.rc_data = StrictRedis(
            host=common_settings["redis_config"]["hostname"],
            port=common_settings["redis_config"]["port"],
            password=common_settings["redis_config"]["password"],
            db=common_settings["redis_config"]["db_data"],
            decode_responses=True
        )

        self.rc_latency = StrictRedis(
            host=common_settings["redis_config"]["hostname"],
            port=common_settings["redis_config"]["port"],
            password=common_settings["redis_config"]["password"],
            db=common_settings["redis_config"]["db_latency"],
            decode_responses=True
        )

        self.rc_bbox = StrictRedis(
            host=common_settings["redis_config"]["hostname"],
            port=common_settings["redis_config"]["port"],
            password=common_settings["redis_config"]["password"],
            db=common_settings["redis_config"]["db_bbox"],
            decode_responses=True
        )

    def __setup_subscriber(self):
        self.rc_data.delete(self.opt.sub_channel)

        # Dummy set value
        # expired_at = 2 # in seconds
        # redis_set(self.rc_data, self.opt.sub_channel, True, expired_at)
        redis_set(self.rc_data, self.opt.sub_channel, 1)
        # redis_set(self.rc_data, self.opt.sub_channel, False)

    def waiting_frames(self):
        # print("Starting YOLOv3 image detector")
        t0_load_weight = time.time()
        self.__load_weight()
        t_load_weight = time.time() - t0_load_weight
        # print(".. Load `weight` in (%.3fs)" % t_load_weight)

        # Latency: Load YOLOv3 Weight
        t_weight_key = "weight-" + str(self.opt.drone_id)
        redis_set(self.rc_latency, t_weight_key, t_load_weight)
        # print('Latency [Load `weight`]: (%.5fs)' % (t_load_weight))

        t0_load_eval = time.time()
        self.__eval_model()
        t_load_eval_model = time.time() - t0_load_eval
        # print(".. Load function `eval_model` in (%.3fs)" % t_load_eval_model)

        # Latency: Execute Evaluation Model
        t_eval_model_key = "evalModel-" + str(self.opt.drone_id)
        redis_set(self.rc_latency, t_eval_model_key, t_load_eval_model)
        # print('Latency [Load `Eval Model`]: (%.5fs)' % (t_load_eval_model))

        self.__get_names_colors()

        # Setup redis subscriber availability
        self.__setup_subscriber()

        # Waiting for get the image information
        stream_ch = "stream_" + self.opt.sub_channel
        # print("\n### Waiting for get the image information @ Channel `%s`" % stream_ch)
        print("\n[%s] Worker-%s: Ready" % (get_current_time(), self.opt.sub_channel))
        pubsub = self.rc.pubsub()
        pubsub.subscribe([stream_ch])
        for item in pubsub.listen():
            # noinspection PyPackageRequirements
            try:
                fetch_data = json.loads(item['data'])
                frame_id = fetch_data['frame_id']

                # imagezmq: receive image
                image_name, im0s = self.image_hub.recv_image()

                if self.opt.save_original_img:
                    self.__save_results(im0s, None, (self.frame_id+1), tcp_img=True, is_raw=True)

                # Padded resize
                image = letterbox(im0s, new_shape=self.img_size)[0]

                # Convert
                image = image[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
                image = np.ascontiguousarray(image, dtype=np.float16 if self.half else np.float32)  # uint8 to fp16/fp32
                image /= 255.0  # 0 - 255 to 0.0 - 1.0

                # Start processing image
                # print("\nStart processing to get MB-Box.")
                print("[%s] Received frame-%d" % (get_current_time(), int(frame_id)))
                redis_set(self.rc_data, self.opt.sub_channel, 0) # set as `Busy`
                self.__process_detection(image, im0s, frame_id)

                frame_id = str(fetch_data["frame_id"])
                prev_fid = str(self.opt.drone_id) + "-" + str((int(frame_id)-1))

                # Preparing to send the frames.
                if self.mbbox_img is not None:
                    output_path = self.opt.mbbox_output + "/frame-%s.jpg" % frame_id

                    # Try writing synchronously: store ONLY when (frame-1) has been stored
                    while redis_get(self.rc, prev_fid) is None and int(frame_id) > 1:
                        pass

                    # Save MBBox image
                    if self.opt.save_mbbox_img:
                        t0_save_mbbox_img = time.time()
                        cv2.imwrite(output_path, self.mbbox_img)
                        t_save_mbbox_img = time.time() - t0_save_mbbox_img
                        t_save_mbbox_img_key = "save2mmboxIMG-" + str(self.opt.drone_id) + "-" + str(frame_id)
                        redis_set(self.rc_latency, t_save_mbbox_img_key, t_save_mbbox_img)
                        # print('Latency [Save MB-Box Image] of frame-%s: (%.5fs)' % (str(frame_id), t_save_mbbox_img))

                    # Set that this frame has been successfully added
                    expired_at = 20  # in seconds
                    key = str(self.opt.drone_id) + "-" + frame_id
                    redis_set(self.rc, key, True, expired_at)
                else:
                    pass
                    # print("This MB-Box is NONE. nothing to be saved yet.")

                # Restore availibility
                redis_set(self.rc_data, self.opt.sub_channel, 1) # set as `Ready`
                # print("\n### This Worker-%s is ready to serve again. \n\n" % self.opt.sub_channel)
                print("\n[%s] Worker-%s: Ready" % (get_current_time(), self.opt.sub_channel))
                worker_channel = "worker-%s" % self.opt.sub_channel
                pub(self.rc, worker_channel, "ok")

                # Set prev_fid as DONE
                redis_set(self.rc_data, prev_fid, None) # set as `Ready`
            except:
                pass


    def __save_latency_to_csv(self):
        save_to_csv(self.opt.latency_output, self.csv_inference, self.time_inference_list)
        save_to_csv(self.opt.latency_output, self.csv_nms, self.time_nms_list)
        save_to_csv(self.opt.latency_output, self.csv_mbbox, self.time_mbbox_list)
        save_to_csv(self.opt.latency_output, self.csv_default, self.time_default_list)

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

    def __save_cropped_img(self, xyxy, im0, idx):
        if self.opt.save_crop_img:
            numpy_xyxy = torch2numpy(xyxy, int)
            xywh = np_xyxy2xywh(numpy_xyxy)
            crop_image(self.save_path, im0, xywh, idx)

    def __save_results(self, im0, vid_cap, frame_id, tcp_img=False, is_raw=False):
        # Save results (image with detections)
        if self.save_img:
            if tcp_img:
                if is_raw:
                    frame_save_path = self.opt.frames_dir + "/frame-%s.jpg" % str(frame_id)
                    if self.opt.save_original_img:
                        cv2.imwrite(frame_save_path, im0)
                else:
                    frame_save_path = self.opt.bbox_dir + "/frame-%s.jpg" % str(frame_id)
                    if self.opt.save_bbox_img:
                        cv2.imwrite(frame_save_path, im0)

            elif self.dataset.mode == 'images':
                if self.webcam:
                    frame_save_path = self.opt.bbox_dir + "/frame-%d.jpg" % frame_id
                    if self.mbbox_img is not None:
                        cv2.imwrite(frame_save_path, self.mbbox_img)
                    else:
                        cv2.imwrite(frame_save_path, im0)
                else:
                        cv2.imwrite(self.save_path, im0)
            else:
                if self.vid_path != self.save_path:  # new video
                    self.vid_path = self.save_path
                    if isinstance(self.vid_writer, cv2.VideoWriter):
                        self.vid_writer.release()  # release previous video writer

                    fps = vid_cap.get(cv2.CAP_PROP_FPS)
                    w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    self.vid_writer = cv2.VideoWriter(self.save_path,
                                                      cv2.VideoWriter_fourcc(*self.opt.fourcc), fps, (w, h))
                self.vid_writer.write(im0)

    def __process_detection(self, img, im0s, this_frame_id):
        self.frame_id += 1
        t = time.time()
        # Get detections
        ts_det = time.time()
        img_torch = torch.from_numpy(img) #.to(self.device)
        img = img_torch.to(self.device)
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        try:
            self.pred = self.model(img)[0]
        except Exception as e:
            print("EEEROR: ", e)
        # t_inference = time.time() - ts_det
        t_inference = (time.time() - ts_det) * 1000  # to ms
        self.time_inference += t_inference
        self.time_inference_list.append(t_inference)

        # Latency: Inference
        # print('Latency [Inference] of frame-%s: (%.5fs)' % (str(this_frame_id), t_inference))
        # cur_time = get_current_time()
        print('[%s] DONE Inference of frame-%s (%.3f ms)' % (get_current_time(), str(this_frame_id), t_inference))
        t_inference_key = "inference-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
        redis_set(self.rc_latency, t_inference_key, t_inference)

        # Default: Disabled
        if self.opt.half:
            self.pred = self.pred.float()

        # Apply NMS: Non-Maximum Suppression
        ts_nms = time.time()
        # to Removes detections with lower object confidence score than 'conf_thres'
        self.pred = non_max_suppression(self.pred, self.opt.conf_thres, self.opt.iou_thres,
                                        classes=self.opt.classes,
                                        agnostic=self.opt.agnostic_nms)
        # print('\n # Total Non-Maximum Suppression (NMS) time: (%.3fs)' % (time.time() - ts_nms))
        t_nms = time.time() - ts_nms
        self.time_nms += t_nms
        self.time_nms_list.append(t_nms)

        # Latency: NMS
        # print('Latency [NMS] of frame-%s: (%.5fs)' % (str(this_frame_id), t_nms))
        t_nms_key = "nms-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
        redis_set(self.rc_latency, t_nms_key, t_nms)

        # Apply Classifier: Default DISABLED
        if self.classify:
            self.pred = apply_classifier(self.pred, self.modelc, img, im0s)

        # Process detections
        '''
        p = path
        s = string for printing
        im0 = image (matrix)
        '''

        try:
            for i, det in enumerate(self.pred):  # detections per image
                self.save_path = self.opt.output + "/" + str(this_frame_id) + ".png"
                self.str_output += '%gx%g ' % img.shape[2:]  # print string
                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0s.shape).round()

                    ts_mbbox = time.time()
                    if self.opt.mbbox_detection:
                        self.__mbbox_detection(det, im0s, this_frame_id)  # modifying Mb-box
                    t_mbbox = time.time() - ts_mbbox
                    self.time_mbbox += t_mbbox
                    self.time_mbbox_list.append(t_mbbox)

                    # Store total processed frames
                    self.total_proc_frames += 1
                    t_proc_frames_key = "total-proc-frames-w%s-%s" % (str(self.opt.sub_channel), str(self.opt.drone_id))
                    store_latency(self.rc_latency, t_proc_frames_key, self.total_proc_frames)

                    # FPS each worker
                    fps_worker_key = "fps-worker-%s" % str(self.opt.sub_channel)
                    _, current_fps_worker = store_fps(self.rc_latency, fps_worker_key, self.opt.drone_id,
                                                      total_frames=self.total_proc_frames)
                    # print('Current [FPS of Worker-%s] with total %d frames: (%.2f fps)' % (
                    #         self.opt.sub_channel, self.total_proc_frames, current_fps_worker))

                    if not self.opt.maximize_latency:
                        if self.opt.default_detection:
                            self.__default_detection(det, im0s, this_frame_id)
                    t_default = time.time() - ts_det - t_mbbox
                    self.time_default += t_default
                    self.time_default_list.append(t_default)

                    # Latency: Default Detection
                    # print('Latency [Default Detection] of frame-%s: (%.5fs)' % (str(this_frame_id), t_default))
                    t_default_key = "draw2bbox-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                    store_latency(self.rc_latency, t_default_key, t_default)
                    # redis_set(self.rc_latency, t_default_key, t_default)

                    # Print time (inference + NMS)
                    # print('%sDone. (%.3fs)' % (self.str_output, time.time() - t))

                    # print('Done. (%.3fs) --> '
                    #       'Inference(%.3fs); NMS(%.3fs); MB-Box(%.3fs); Default-Bbox(%.3fs)' %
                    #       ((time.time() - t),
                    #        t_inference, t_nms, t_mbbox, t_default))

                    # Save end latency calculation
                    t_end_key = "end-" + str(self.opt.drone_id)
                    # redis_set(self.rc_latency, t_end_key, time.time())
                    store_latency(self.rc_latency, t_end_key, time.time())

                    # Mark last processed frame
                    t_last_frame_key = "last-" + str(self.opt.drone_id)
                    # redis_set(self.rc_latency, t_last_frame_key, int(this_frame_id))
                    store_latency(self.rc_latency, t_last_frame_key, int(this_frame_id))

                    # # latency: End-to-end Latency, each frame
                    # t_sframe_key = "start-fi-" + str(self.opt.drone_id)  # to calculate end2end latency each frame.
                    # t_end2end_frame = redis_get(self.rc_latency, t_end_key) - redis_get(self.rc_latency, t_sframe_key)
                    # t_e2e_frame_key = "end2end-frame-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                    # redis_set(self.rc_latency, t_e2e_frame_key, t_end2end_frame)
                    # print('\nLatency [End2end this frame] of frame-%s: (%.5fs)' % (str(this_frame_id), t_end2end_frame))

                    # Save BBox image
                    self.__save_results(im0s, None, self.frame_id, tcp_img=True)

                    # Get total captured frames
                    # t_total_frames_key = "total-frames-" + str(self.opt.drone_id)
                    # total_frames = redis_get(self.rc_latency, t_total_frames_key)

                    # latency: End-to-end Latency TOTAL
                    # t_start_key = "start-" + str(self.opt.drone_id)
                    # t_end2end = redis_get(self.rc_latency, t_end_key) - redis_get(self.rc_latency, t_start_key)
                    # t_e2e_key = "end2end-" + str(self.opt.drone_id)
                    # redis_set(self.rc_latency, t_e2e_key, t_end2end)
                    # # print('\nLatency [E2E] of frame-%s: (%.5fs)' % (str(this_frame_id), t_end2end))
                    # print('Latency [E2E] with total %d frames: (%.5fs); Now in frame=%d' %
                    #       (total_frames, t_end2end, this_frame_id))

                    # Calculate current FPS
                    # time_per_frame = total_frames / t_end2end
                    # current_fps = 1000 / time_per_frame
                    # current_fps = round(current_fps, 2)
                    # fps_key = "fps-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                    # total_frames, current_fps = store_fps(self.rc_latency, fps_key, self.opt.drone_id)
                    # print('Current [FPS] with total %d frames: (%.2f fps)' % (total_frames, current_fps))
                    # # redis_set(self.rc_latency, fps_key, current_fps)

                    # Publish to PLF (PiH Location Fetcher) to notify that it's done.
                    plf_detection_channel = "PLF-%d-%d" % (self.opt.drone_id, this_frame_id)
                    redis_set(self.rc_data, plf_detection_channel, True, 10)  # expired in 10 seconds

        except Exception as e:
            print("ERROR Pred: ", e)

    def __default_detection(self, det, im0, this_frame_id):
        if self.opt.default_detection:
            original_img = im0.copy()

            # Print results
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                self.str_output += '%g %ss, ' % (n, self.names[int(c)])  # add to string

            # Write results
            idx_detected = 0
            bbox_data = []
            for *xyxy, conf, cls in det:
                numpy_xyxy = get_det_xyxy(xyxy)
                this_label = '%s %.2f' % (self.names[int(cls)], conf)
                this_color = self.colors[int(cls)]
                idx_detected += 1
                self.save_txt = True  # Ardi: manually added

                # Save cropped files
                self.__save_cropped_img(xyxy, original_img, idx_detected)

                this_bbox = {
                    "obj_idx": idx_detected,
                    "xyxy": [str(val) for val in numpy_xyxy],
                    "label": this_label,
                    "color": [str(color) for color in this_color]
                }
                bbox_data.append(this_bbox)

                # disable plot bbox, since PiH Location Fetcher will do the work!
                # if self.save_img or self.view_img:  # Add bbox to image
                #     plot_one_box(xyxy, im0, label=this_label, color=this_color)

            # store bbox information
            self.__store_mbbox_coord(this_frame_id, bbox_data, is_reg_bbox=True)

    '''
    FYI:
        Variable `det` consists of three parameters:
        1. *xyxy : Coordinate of (x1, y1) and (x2, y2)
        2. conf  : Confidence Score
        3. cls   : Class (`Person` and `Flag`)
    '''
    def __mbbox_detection(self, det, im0, this_frame_id):
        # print(" ### @ __mbbox_detection")
        # if self.mbbox_algorithm:
        if self.opt.mbbox_detection:
            # ts_copy_img = time.time()
            original_img = im0.copy()
            # t_copy_img = time.time() - ts_copy_img
            # print('\n**** Proc. Latency [Copy IMG] of frame-%s: (%.5fs)' % (str(this_frame_id), t_copy_img))

            # Sementara masih error; abaikan
            if self.opt.modv1:
                ts_mod_v1 = time.time()
                self.mbbox = MODv1(self.webcam, im0, self.opt, self.save_path, det, original_img, self.names,
                                   self.w_ratio, self.h_ratio)
                self.mbbox.run()

                if not self.opt.modv2:
                    self.detected_mbbox = self.mbbox.get_detected_mbbox()
                    self.mbbox_img = self.mbbox.get_mbbox_img()
                    self.__store_mbbox_coord(this_frame_id, self.detected_mbbox)  # store mbbox information
                    self.__safety_store_txt()

                t_mod_v1 = time.time() - ts_mod_v1
                # Latency: save Proc. Latency MODv1
                t_modv1_key = "modv1-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                print('Latency [MODv1] of frame-%d: (%.5fs)' % (this_frame_id, t_mod_v1))
                redis_set(self.rc_latency, t_modv1_key, t_mod_v1)

            if self.opt.modv2:
                ts_mod_v2 = time.time()
                self.mbbox = MODv2(self.webcam, im0, self.opt, self.save_path, det, original_img, self.names)
                self.mbbox.run()
                self.detected_mbbox = self.mbbox.get_detected_mbbox()  # xyxy(s)
                self.mbbox_img = self.mbbox.get_mbbox_img()  # image
                self.__store_mbbox_coord(this_frame_id, self.detected_mbbox)  # store mbbox information
                self.__safety_store_txt()

                t_mod_v2 = time.time() - ts_mod_v2
                # Latency: save Proc. Latency MODv2
                t_modv2_key = "modv2-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                # print('Latency [MODv2] of frame-%d: (%.5fs)' % (this_frame_id, t_mod_v2))
                redis_set(self.rc_latency, t_modv2_key, t_mod_v2)

    def __safety_store_txt(self):
        if len(self.detected_mbbox) == 0:
            if self.opt.output_txt:
                save_txt(self.save_path, self.opt.txt_format)
        else:
            if self.detected_mbbox is not None:
                for i in range(len(self.detected_mbbox)):
                    mbbox_xyxy = self.detected_mbbox[i]
                    if self.opt.output_txt:
                        save_txt(self.save_path, self.opt.txt_format, mbbox_xyxy)

    # Key = `<drone_id>-<frame_id>-mbbox`
    def __store_mbbox_coord(self, frame_id, this_mbbox, is_reg_bbox=False):
        this_mbbox = this_mbbox if this_mbbox is not None else []
        if not is_reg_bbox:
            mbbox_dict = mbboxlist2dict(this_mbbox)
        else:
            mbbox_dict = this_mbbox
        if is_reg_bbox:
            suffix = "-bbox"
        else:
            suffix = "-mbbox"
        key = "d" + str(self.opt.drone_id) + "-f" + str(frame_id) + suffix
        p_mbbox_coord = json.dumps(mbbox_dict)
        redis_set(self.rc_bbox, key, p_mbbox_coord)

        # print(" ------ mbbox_dict:", mbbox_dict)
        # print(" HARUSNYA coords key: ", suffix, key, p_mbbox_coord)

        test_data = redis_get(self.rc_bbox, key)
        # print(" STORED coords key: ", suffix, key, test_data)
