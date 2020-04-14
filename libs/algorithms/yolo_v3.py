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
from libs.addons.redis.translator import redis_set, redis_get
from libs.algorithms.behavior_detection import BehaviorDetection

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

        # (320, 192) or (416, 256) or (608, 352) for (height, width)
        self.img_size = (320, 192) if ONNX_EXPORT else opt.img_size

        self.out, self.source, self.weights, self.half, self.view_img, self.save_txt = opt.output, opt.source, opt.weights, opt.half, opt.view_img, opt.save_txt
        self.webcam = self.source == '0' or self.source.startswith('rtsp') or self.source.startswith('http') or self.source.endswith('.txt')

        # Initialize
        self.device = torch_utils.select_device(device='cpu' if ONNX_EXPORT else opt.device)
        if os.path.exists(self.out):
            shutil.rmtree(self.out)  # delete output folder
        os.makedirs(self.out)  # make new output folder
        os.makedirs(self.out+"/enlarge")  # make enlarge folder
        os.makedirs(self.out+"/mbbox")  # make mbbox folder

        # Empty folders
        mbbox_folder = opt.mbbox_output + str(opt.drone_id)
        if os.path.exists(mbbox_folder):
            shutil.rmtree(mbbox_folder)  # delete output folder
        os.makedirs(mbbox_folder)  # make new output folder

        # Initialize model
        self.model = Darknet(opt.cfg, self.img_size)
        self.mbbox = None # Merge Bounding Box
        self.detected_mbbox = 0

        # Sef Default Detection Algorithms
        # self.default_algorithm = opt.default_detection
        self.mbbox_algorithm = opt.mbbox_detection

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

    def run(self):
        print("Starting YOLO-v3 Detection Network")
        self.__load_weight()
        self.__second_stage_classifier()
        self.__eval_model()
        # self.__export_mode() # TBD
        self.__half_precision()
        self.__set_data_loader()
        self.__get_names_colors()

        # if self.opt.output_txt:
        #     self.__print_save_txt_img()

        self.__iterate_frames() # Perform detection in each frame here
        self.__save_latency_to_csv()

        print('\nFinished. Total elapsed time: (%.3fs) --> '
              'Inference(%.3fs); NMS(%.3fs); MB-Box(%.3fs)' %
              ((time.time() - self.t0), self.time_inference, self.time_nms, self.time_mbbox))

    def __setup_subscriber(self):
        self.rc_data.delete(self.opt.sub_channel)

        # Dummy set value
        # expired_at = 2 # in seconds
        # redis_set(self.rc_data, self.opt.sub_channel, True, expired_at)
        redis_set(self.rc_data, self.opt.sub_channel, 1)
        # redis_set(self.rc_data, self.opt.sub_channel, False)

    def waiting_frames(self):
        print("Starting YOLOv3 image detector")
        t0 = time.time()
        self.__load_weight()
        t_load_weight = time.time() - t0
        # print(".. Load `weight` in (%.3fs)" % t_load_weight)

        # Latency: Load YOLOv3 Weight
        t_weight_key = "weight-" + str(self.opt.drone_id)
        redis_set(self.rc_latency, t_weight_key, t_load_weight)
        print('\nLatency [Load `weight`]: (%.5fs)' % (t_load_weight))

        t0 = time.time()
        self.__eval_model()
        t_load_eval_model = time.time() - t0
        # print(".. Load function `eval_model` in (%.3fs)" % t_load_eval_model)

        # Latency: Execute Evaluation Model
        t_eval_model_key = "evalModel-" + str(self.opt.drone_id)
        redis_set(self.rc_latency, t_eval_model_key, t_load_eval_model)
        print('\nLatency [Load `Eval Model`]: (%.5fs)' % (t_load_eval_model))

        self.__get_names_colors()

        # Setup redis subscriber availability
        self.__setup_subscriber()

        # Waiting for get the image information
        stream_ch = "stream_" + self.opt.sub_channel
        print("\n### Waiting for get the image information @ Channel `%s`" % stream_ch)
        pubsub = self.rc.pubsub()
        pubsub.subscribe([stream_ch])
        for item in pubsub.listen():
            # noinspection PyPackageRequirements
            try:
                t0_sub2frame = time.time()
                # Start fetching information
                fetch_data = json.loads(item['data'])
                frame_id = fetch_data['frame_id']
                # print('Streamer collects : ', fetch_data)

                # Latency: subscribing frame
                t_sub2frame = time.time() - t0_sub2frame
                t_sub2frame_key = "sub2frame-" + str(self.opt.drone_id) + "-" + str(frame_id)
                redis_set(self.rc_latency, t_sub2frame_key, t_sub2frame)
                print('\nLatency [Subscriber extracting information] of frame-%s: (%.5fs)' % (str(frame_id), t_sub2frame))

                self.source = fetch_data["img_path"]
                # print('img_path : ', self.source)
                # Load image from pub: get `img_path`
                t0_load_img = time.time()
                self.__set_data_loader()
                t_load_img = time.time() - t0_load_img
                # print(".. load image into variable in (%.3fs)" % (time.time() - t0))
                t_load_img_key = "loadIMG-" + str(self.opt.drone_id) + "-" + str(frame_id)
                redis_set(self.rc_latency, t_load_img_key, t_load_img)
                print('\nLatency [Loads image into YOLOv3 Worker] of frame-%s: (%.5fs)' % (str(frame_id), t_load_img))

                # # Check worker status first, please wait while still working
                # is_worker_ready = redis_get(self.rc_data, self.opt.sub_channel)
                # print(">>>>>> is_worker_ready = ", is_worker_ready)
                # if is_worker_ready:
                #     print("\nWorker-%d is still running, waiting to finish ..." % self.opt.sub_channel)
                #     time.sleep(0.1)

                # Start processing image
                print("\nStart processing to get MB-Box.")
                redis_set(self.rc_data, self.opt.sub_channel, 0) # set as `Busy`
                # print("Set as busy Done.")
                self.__iterate_frames(frame_id)  # Perform detection in each frame here
                # print(" >>> Hasil MB-Box Img = ", self.mbbox_img)
                # print("Process finished.")

                frame_id = str(fetch_data["frame_id"])
                prev_fid = str(self.opt.drone_id) + "-" + str((int(frame_id)-1))

                # # TBD: Start behavior detection in background process, in every 30 frames (FPS=30)
                # behave_det = BehaviorDetection(self.opt, int(frame_id), self.detected_mbbox)
                # if int(frame_id) % self.fps and self.detected_mbbox > 0:
                #     behave_det.run()

                # Preparing to send the frames.
                if self.mbbox_img is not None:
                    # output_path = self.opt.mbbox_output + "frame-%s.jpg" % frame_id
                    output_path = self.opt.mbbox_output + str(self.opt.drone_id) + "/frame-%s.jpg" % frame_id

                    # Try writing synchronously: store ONLY when (frame-1) has been stored
                    # print(" ######## PREV_ID = ", redis_get(self.rc, prev_fid))
                    while redis_get(self.rc, prev_fid) is None and int(frame_id) > 1:
                        # print(" ######## Waiting previous frame to be stored. PREV_ID = ", redis_get(self.rc, prev_fid))
                        # time.sleep(1)
                        pass

                    t0_save_mbbox_img = time.time()
                    cv2.imwrite(output_path, self.mbbox_img)
                    # print("Saving image in: ", output_path)
                    # print(".. MB-Box image is saved in (%.3fs)" % (time.time() - t0))
                    t_save_mbbox_img = time.time() - t0_save_mbbox_img
                    t_save_mbbox_img_key = "save2mmboxIMG-" + str(self.opt.drone_id) + "-" + str(frame_id)
                    redis_set(self.rc_latency, t_save_mbbox_img_key, t_save_mbbox_img)
                    print('\nLatency [Save MB-Box Image] of frame-%s: (%.5fs)' % (str(frame_id), t_save_mbbox_img))

                    # Set that this frame has been successfully added
                    expired_at = 20  # in seconds
                    key = str(self.opt.drone_id) + "-" + frame_id
                    redis_set(self.rc, key, True, expired_at)
                else:
                    print("This MB-Box is NONE. nothing to be saved yet.")

                # self.__save_latency_to_csv()

                # Restore availibility
                redis_set(self.rc_data, self.opt.sub_channel, 1) # set as `Ready`
                print("\n### This Worker-%s is ready to serve again. \n\n" % self.opt.sub_channel)

                # Set prev_fid as DONE
                redis_set(self.rc_data, prev_fid, None) # set as `Ready`

                # if this is latest frame: Set this frame as latest
                # key = "drone_id-latest", value: "drone_id-frame_id"
                # redis_set(self.rc_data, prev_fid, None) # set as `Ready`
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

    # Executed after detect()
    # def __print_save_txt_img(self):
    #     if self.save_txt or self.save_img:
    #     # if self.save_txt:
    #         print('Results saved to %s' % os.getcwd() + os.sep + self.out)
    #         if platform == 'darwin':  # MacOS
    #             os.system('open ' + self.out + ' ' + self.save_path)

    def __save_cropped_img(self, xyxy, im0, idx):
        if self.opt.crop_img:
            # Try saving cropped image
            original_img = im0.copy()
            numpy_xyxy = torch2numpy(xyxy, int)
            xywh = np_xyxy2xywh(numpy_xyxy)
            crop_image(self.save_path, original_img, xywh, idx)

    def __save_results(self, im0, vid_cap, frame_id):
        # Save results (image with detections)
        if self.save_img:
            if self.dataset.mode == 'images':
                # print("\n #### mode IMAGES: ", self.save_path)
                # print("\n #### im0: ", im0)

                if self.webcam:
                    frame_save_path = self.opt.frames_dir + "/frame-%d.jpg" % frame_id
                    # frame_save_path = self.opt.frames_dir + "/frame-%d.png" % frame_id
                    if self.mbbox_img is not None:
                        cv2.imwrite(frame_save_path, self.mbbox_img)
                    else:
                        cv2.imwrite(frame_save_path, im0)
                else:
                        cv2.imwrite(self.save_path, im0)
                # save_path = self.save_path
                # crop_save_path = save_path.replace('.png', '') + "-%d.png" % frame_id
                # cv2.imwrite(crop_save_path, im0)
                # print("#### Image @ frame-%d saved." % frame_id)
            else:
                # print("\n #### mode Bukan IMAGES")
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

    def __feed_video_frames(self):
        self.t0 = time.time()
        # frame_id = 0
        for path, img, im0s, vid_cap in self.dataset:
            self.frame_id += 1

            if self.webcam:
                frame_save_path = self.opt.frames_dir + "/frame-%d.jpg" % self.frame_id
                cv2.imwrite(frame_save_path, img)

            if self.frame_id > 10:
                self.manual_stop = True
                print("\n\n #### FORCED TO BREAK HERE !!!")
                break

    def __iterate_frames(self, this_frame_id=None):
        # Run inference
        self.t0 = time.time()
        # frame_id = 0
        for path, img, im0s, vid_cap in self.dataset:
            self.frame_id += 1
            t = time.time()

            # Get detections
            ts_det = time.time()
            img = torch.from_numpy(img).to(self.device)
            if img.ndimension() == 3:
                img = img.unsqueeze(0)
            self.pred = self.model(img)[0]
            # print('\n # Total Inference time: (%.3fs)' % (time.time() - ts_det))
            t_inference = time.time() - ts_det
            self.time_inference += t_inference
            self.time_inference_list.append(t_inference)

            # Latency: Inference
            print('\nLatency [Inference] of frame-%s: (%.5fs)' % (str(this_frame_id), t_inference))
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
            print('\nLatency [NMS] of frame-%s: (%.5fs)' % (str(this_frame_id), t_nms))
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

            for i, det in enumerate(self.pred):  # detections per image
                if self.webcam:  # batch_size >= 1
                    p, self.str_output, im0 = path[i], '%g: ' % i, im0s[i]
                else:
                    p, self.str_output, im0 = path, '', im0s

                self.save_path = str(Path(self.out) / Path(p).name)
                self.str_output += '%gx%g ' % img.shape[2:]  # print string
                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    ts_mbbox = time.time()
                    if self.mbbox_algorithm:
                        self.__mbbox_detection(det, im0, this_frame_id) # modifying Mb-box
                    t_mbbox = time.time() - ts_mbbox
                    self.time_mbbox += t_mbbox
                    self.time_mbbox_list.append(t_mbbox)

                    # Latency: MB-Box
                    print('\nLatency [MB-Box Algorithm] of frame-%s: (%.5fs)' % (str(this_frame_id), t_mbbox))
                    t_mbbox_key = "mbbox-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                    redis_set(self.rc_latency, t_mbbox_key, t_mbbox)

                    ts_default = time.time()
                    if not self.opt.maximize_latency:
                        if self.opt.default_detection:
                            self.__default_detection(det, im0)
                    t_default = time.time() - ts_default
                    self.time_default += t_default
                    self.time_default_list.append(t_default)

                    # Latency: Default Detection
                    print('\nLatency [Default Detection] of frame-%s: (%.5fs)' % (str(this_frame_id), t_default))
                    t_default_key = "draw2bbox-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                    redis_set(self.rc_latency, t_default_key, t_default)

                    # Print time (inference + NMS)
                    # print('%sDone. (%.3fs)' % (self.str_output, time.time() - t))

                    print('Done. (%.3fs) --> '
                          'Inference(%.3fs); NMS(%.3fs); MB-Box(%.3fs); Default-Bbox(%.3fs)' %
                          ((time.time() - t),
                           t_inference, t_nms, t_mbbox, t_default))

                    # Save end latency calculation
                    t_end_key = "end-" + str(self.opt.drone_id)
                    redis_set(self.rc_latency, t_end_key, time.time())

                    # Mark last processed frame
                    t_last_frame_key = "last-" + str(self.opt.drone_id)
                    redis_set(self.rc_latency, t_last_frame_key, int(this_frame_id))

                    # latency: End-to-end Latency, each frame
                    t_sframe_key = "start-fi-" + str(self.opt.drone_id)  # to calculate end2end latency each frame.
                    t_end2end_frame = redis_get(self.rc_latency, t_end_key) - redis_get(self.rc_latency, t_sframe_key)
                    t_e2e_frame_key = "end2end-frame-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                    redis_set(self.rc_latency, t_e2e_frame_key, t_end2end_frame)
                    print('\nLatency [End2end this frame] of frame-%s: (%.5fs)' % (str(this_frame_id), t_end2end_frame))

                    # latency: End-to-end Latency TOTAL
                    t_start_key = "start-" + str(self.opt.drone_id)
                    t_end2end = redis_get(self.rc_latency, t_end_key) - redis_get(self.rc_latency, t_start_key)
                    t_e2e_key = "end2end-" + str(self.opt.drone_id)
                    redis_set(self.rc_latency, t_e2e_key, t_end2end)
                    print('\nLatency [This End2end] of frame-%s: (%.5fs)' % (str(this_frame_id), t_end2end))

                    # Stream results
                    # if self.view_img:
                    #     cv2.imshow(p, im0)
                    #     if cv2.waitKey(1) == ord('q'):  # q to quit
                    #         raise StopIteration

                    self.__save_results(im0, vid_cap, self.frame_id)
            # print('\n # Total MB-Box time: (%.3fs)' % (time.time() - ts_mbbox))


    def __default_detection(self, det, im0):
        if self.opt.default_detection:
            original_img = im0.copy()

            # Print results
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                self.str_output += '%g %ss, ' % (n, self.names[int(c)])  # add to string

            # Write results
            idx_detected = 0
            for *xyxy, conf, cls in det:
                idx_detected += 1
                self.save_txt = True  # Ardi: manually added

                # Save cropped files
                self.__save_cropped_img(xyxy, original_img, idx_detected)

                # print(">>>>>>>>>>>>> PLOT BBOX aja self.save_img = ", self.save_img)
                if self.save_img or self.view_img:  # Add bbox to image
                    label = '%s %.2f' % (self.names[int(cls)], conf)
                    plot_one_box(xyxy, im0, label=label+"-IDX="+str(idx_detected-1), color=self.colors[int(cls)])

    '''
    FYI:
        Variable `det` consists of three parameters:
        1. *xyxy : Coordinate of (x1, y1) and (x2, y2)
        2. conf  : Confidence Score
        3. cls   : Class (`Person` and `Flag`)
    '''
    def __mbbox_detection(self, det, im0, this_frame_id):
        if self.mbbox_algorithm:
            ts_copy_img = time.time()
            original_img = im0.copy()
            t_copy_img = time.time() - ts_copy_img
            # print('\n**** Proc. Latency [Copy IMG] of frame-%s: (%.5fs)' % (str(this_frame_id), t_copy_img))

            if self.opt.modv1:
                ts_mod_v1 = time.time()
                self.mbbox = MODv1(self.webcam, im0, self.opt, self.save_path, det, original_img, self.names,
                                   self.w_ratio, self.h_ratio)
                self.mbbox.run()
                if not self.opt.modv2:
                    self.detected_mbbox = self.mbbox.get_detected_mbbox()
                    self.mbbox_img = self.mbbox.get_mbbox_img()

                    for i in range(len(self.detected_mbbox)):
                        mbbox_xyxy = self.detected_mbbox[i]
                        if self.opt.output_txt:
                            save_txt(self.save_path, self.opt.txt_format, mbbox_xyxy, 'w+')
                t_mod_v1 = time.time() - ts_mod_v1
                # print('\n~Proc. Latency [MODv1] of frame-%s: (%.5fs)' % (str(this_frame_id), t_mod_v1))

                # Latency: save Proc. Latency MODv1
                t_modv1_key = "modv1-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                print('\nLatency [MODv1] of frame-%d: (%.5fs)' % (this_frame_id, t_mod_v1))
                redis_set(self.rc_latency, t_modv1_key, t_mod_v1)

            if self.opt.modv2:
                ts_mod_v2 = time.time()
                self.mbbox = MODv2(self.webcam, im0, self.opt, self.save_path, det, original_img, self.names)
                self.mbbox.run()
                self.detected_mbbox = self.mbbox.get_detected_mbbox()  # xyxy(s)
                self.mbbox_img = self.mbbox.get_mbbox_img()  # image

                if len(self.detected_mbbox) == 0:
                    if self.opt.output_txt:
                        save_txt(self.save_path, self.opt.txt_format)
                else:
                    for i in range(len(self.detected_mbbox)):
                        mbbox_xyxy = self.detected_mbbox[i]
                        if self.opt.output_txt:
                            save_txt(self.save_path, self.opt.txt_format, mbbox_xyxy)
                            # save_txt(self.save_path, self.opt.txt_format, mbbox_xyxy, 'w+')

                # print(" #### List of self.detected_mbbox:", self.detected_mbbox)
                # print(" #### self.mbbox_img:", self.mbbox_img)
                t_mod_v2 = time.time() - ts_mod_v2
                # print('~Proc. Latency [MODv2] of frame-%s: (%.5fs)' % (str(this_frame_id), t_mod_v2))

                # Latency: save Proc. Latency MODv2
                t_modv2_key = "modv2-" + str(self.opt.drone_id) + "-" + str(this_frame_id)
                print('\nLatency [MODv2] of frame-%d: (%.5fs)' % (this_frame_id, t_mod_v2))
                redis_set(self.rc_latency, t_modv2_key, t_mod_v2)

    def get_mbbox_img(self):
        return self.mbbox_img