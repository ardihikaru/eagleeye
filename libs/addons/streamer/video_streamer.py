import cv2 as cv
import imagezmq
from libs.addons.redis.translator import redis_get, redis_set, pub
from libs.addons.redis.utils import store_latency, store_fps
from libs.settings import common_settings
from libs.addons.redis.my_redis import MyRedis
from libs.algorithms.pih_location_fetcher import PIHLocationFetcher
from models import *  # set ONNX_EXPORT in models.py
from utils.datasets import *
import simplejson as json
from imutils.video import FileVideoStream


class VideoStreamer(MyRedis):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        self.save_path = opt.output_folder
        # self.__set_redis()

        self.is_running = True
        self.max_frames = opt.max_frames
        self.start_frame_id = opt.start_frame_id

        # set waiting time based on the worker type: CPU or GPU
        self.device = torch_utils.select_device(device='cpu' if ONNX_EXPORT else opt.device)
        # heartbeat msg to check worker status
        if self.device == "cuda":
            self.wait_time = common_settings["redis_config"]["heartbeat"]["gpu"]
        else:
            self.wait_time = common_settings["redis_config"]["heartbeat"]["cpu"]

        self.worker_id = 0  # reset, when total workers = `self.opt.total_workers`

        # Empty folders
        # out_folder = opt.output_folder + str(opt.drone_id)
        out_folder = opt.output_folder
        if os.path.exists(out_folder):
            shutil.rmtree(out_folder)  # delete output folder
        os.makedirs(out_folder)  # make new output folder

        self.zmq_sender = []
        self.__set_zmq_worker_sender()
        self.__set_zmq_plf_sender()
        self.__set_zmq_visualizer_sender()

        self.total_pih_candidates = 0
        self.period_pih_candidates = []

    def __set_zmq_worker_sender(self):
        for i in range(int(self.opt.total_workers)):
            url = 'tcp://127.0.0.1:555' + str((i + 1))
            sender = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
            self.zmq_sender.append(sender)

    # PiH Location Fetcher (plf)
    def __set_zmq_plf_sender(self):
        url = 'tcp://127.0.0.1:' + str(self.opt.pih_location_fetcher_port)
        self.frame_sender = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
        self.plf_send_status_channel = "plf-send-status"

    def __set_zmq_visualizer_sender(self):
        url = 'tcp://127.0.0.1:' + str(self.opt.visualizer_origin_port)
        self.frame_sender_visualizer = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
        self.visualizer_channel = "visualizer-origin-" + str(self.opt.drone_id)

    def run(self):
        if self.opt.source_type == "folder":
            print("\nReading folder:")

            t_stream_setup_key = "stream-start-" + str(self.opt.drone_id)
            redis_set(self.rc_latency, t_stream_setup_key, time.time())
            self.detect_from_folder()

        else:
            print("\nReading video:")
            while self.is_running:
                try:
                    # self.cap = cv.VideoCapture(self.opt.source)
                    # self.cap = cv.VideoCapture(self.opt.source)
                    self.cap = FileVideoStream(self.opt.source).start()
                    self.__start_streaming()
                except:
                    print("\nUnable to communicate with the Streaming. Restarting . . .")
                    # The following frees up resources and closes all windows
                    self.cap.release()

    def __get_ordered_img(self, dataset):
        max_img = len(dataset)
        ordered_dataset = []
        for i in range(max_img):
            ordered_dataset.append([])

        i = 0
        for path, img, im0s, vid_cap in dataset:
            prefix = self.opt.source_folder_prefix
            removed_str = self.opt.source + prefix
            real_frame_idx = int((path.replace(removed_str, "")).replace(".png", ""))
            real_idx = real_frame_idx - 1
            ordered_dataset[real_idx] = [path, img, im0s, vid_cap]
            i += 1

        return ordered_dataset

    def detect_from_folder(self):
        n = 0
        frame_id = 0
        received_frame_id = 0

        # Set Dataloader
        dataset = LoadImages(self.opt.source, img_size=self.opt.img_size, half=self.opt.half)

        # Save timestamp to start extracting video streaming.
        t_start_key = "start-" + str(self.opt.drone_id)
        redis_set(self.rc_latency, t_start_key, time.time())

        # order image index
        ordered_dataset = self.__get_ordered_img(dataset)

        for i in range(len(ordered_dataset)):
            received_frame_id, path, img, im0s, vid_cap = (i + 1), ordered_dataset[i][0], ordered_dataset[i][1], \
                                                          ordered_dataset[i][2], ordered_dataset[i][3]

            # Store total captured frames
            t_total_frames_key = "total-frames-" + str(self.opt.drone_id)
            redis_set(self.rc_latency, t_total_frames_key, received_frame_id)

            t_sframe_key = "start-fi-" + str(self.opt.drone_id)  # to calculate end2end latency each frame.
            redis_set(self.rc_latency, t_sframe_key, time.time())
            n += 1

            # ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
            try:
                t0_frame = time.time()
                ret, frame = True, im0s

                n, frame_id, is_break = self.__process_image(ret, frame, frame_id,
                                                             t0_frame, received_frame_id, n)

                if is_break:
                    break

            except Exception as e:
                print(" ---- e:", e)
                if not self.opt.auto_restart:
                    print("\nStopping the system. . .")
                    time.sleep(common_settings["streaming_config"]["delay_disconnected"])
                    self.is_running = False
                else:
                    print("No more frame to show.")
                break

    def __reset_worker(self):
        if self.worker_id == self.opt.total_workers:
            self.worker_id = 0

    # None = DISABLED; 1=Ready; 0=Busy
    def __worker_status(self):
        return redis_get(self.rc_data, self.worker_id)

    # Find any other available worker instead.
    def __find_optimal_worker(self):
        pass
        # finally, set avalaible worker_id into `self.worker_id`
        # when all N workers are OFF, force stop this System!

    def __worker_finder_v1(self):
        while self.__worker_status() == 0:
            if not self.opt.disable_delay:
                time.sleep(self.wait_time)
        return time.time()

    # use pubsub instead of infinite loop
    def __worker_finder_v2(self):
        if self.__worker_status() == 0:
            pub_sub_sender = self.rc.pubsub()
            worker_channel = "worker-%d" % self.worker_id
            pub_sub_sender.subscribe([worker_channel])
            for item in pub_sub_sender.listen():
                if isinstance(item["data"], int):
                    pass
                else:
                    break
        return time.time()

    def __load_balancing(self, frame_id, frame):
        # Initially, send process into first worker
        self.worker_id += 1
        stream_channel = common_settings["redis_config"]["channel_prefix"] + str(self.worker_id)

        # Check worker status first, please wait while worker-n still working
        # TBD
        if redis_get(self.rc_data, self.worker_id) is None:
            print("This worker is OFF. Nothing to do")
            print("TBD next time: Should skip this worker and move to the next worker instead")
            self.__find_optimal_worker()
        else:
            # None = DISABLED; 1=Ready; 0=Busy
            t0_wait = time.time()
            # t1_wait = self.__worker_finder_v1()
            t1_wait = self.__worker_finder_v2()
            t_wait = round(((t1_wait - t0_wait) * 1000), 2)
            print("[%s] Assign D%d-frame-%d into worker-%s (waiting time: %s ms)" %
                  (get_current_time(), self.opt.drone_id, frame_id, self.worker_id, t_wait))

            data = {
                "frame_id": frame_id,
                "worker_id": self.worker_id
            }
            p_mdata = json.dumps(data)

            # Configure ZMQ & Redis Pub/Sub parameters
            # Send frame into ZMQ channel
            t0_zmq = time.time()
            zid = self.worker_id - 1

            self.zmq_sender[zid].send_image(str(frame_id), frame)
            t_recv = time.time() - t0_zmq
            # print('Latency [Send imagezmq] of frame-%s: (%.5fs)' % (str(frame_id), t_recv))

            # Latency: capture publish frame information
            t0_pub2frame = time.time()
            pub(self.rc_data, stream_channel, p_mdata)
            t_pub2frame = time.time() - t0_pub2frame
            # print('Latency [Publish frame info] of frame-%s: (%.5fs)' % (str(frame_id), t_pub2frame))
            t_pub2frame_key = "pub2frame-" + str(self.opt.drone_id) + "-" + str(frame_id)
            redis_set(self.rc_data, t_pub2frame_key, t_pub2frame)

            redis_set(self.rc_data, self.worker_id, 0)  # set this worker unavailable

        self.__reset_worker()

        # FPS load frame of each worker
        fps_lb_key = "fps-load-balancer-%s" % str(self.opt.drone_id)
        total_frames, current_fps = store_fps(self.rc_latency, fps_lb_key, self.opt.drone_id)
        # print('Current [FPS Load Balancer of Drone-%d] with total %d frames: (%.2f fps)' % (
        #     self.opt.drone_id, total_frames, current_fps))

    def __start_streaming(self):
        n = 0
        frame_id = 0
        received_frame_id = 0

        # Save timestamp to start extracting video streaming.
        t_start_key = "start-" + str(self.opt.drone_id)
        redis_set(self.rc_latency, t_start_key, time.time())

        # while (self.cap.isOpened()) and self.is_running:
        while (self.cap.more()) and self.is_running:
            received_frame_id += 1

            # Store total captured frames
            t_total_frames_key = "total-frames-" + str(self.opt.drone_id)
            redis_set(self.rc_latency, t_total_frames_key, received_frame_id)

            t_sframe_key = "start-fi-" + str(self.opt.drone_id)  # to calculate end2end latency each frame.
            redis_set(self.rc_latency, t_sframe_key, time.time())
            n += 1

            # ret = a boolean return value from getting the frame,
            # frame = the current frame being projected in the video
            try:
                t0_frame = time.time()
                # ret, frame = self.cap.read()
                ret = True
                frame = self.cap.read()

                # t0 each frame
                t0_frame_key = "t0-frame-" + str(self.opt.drone_id) + "-" + str(frame_id)
                redis_set(self.rc_latency, t0_frame_key, time.time())

                n, frame_id, is_break = self.__process_image(ret, frame, frame_id,
                                                             t0_frame, received_frame_id, n)

                if is_break:
                    break

            except Exception as e:
                print(" ---- e:", e)
                if not self.opt.auto_restart:
                    print("\nStopping the system. . .")
                    time.sleep(7)
                    self.is_running = False
                else:
                    print("No more frame to show.")
                break

    def __process_image(self, ret, frame, frame_id, t0_frame, received_frame_id, n):
        # Latency: capture each frame
        t_frame = time.time() - t0_frame
        # print('Latency [Reading stream frame] of frame-%d: (%.5fs)' % (received_frame_id, t_frame))

        t_frame_key = "frame-" + str(self.opt.drone_id) + "-" + str(frame_id)
        redis_set(self.rc_latency, t_frame_key, t_frame)
        is_break = False

        if n == self.opt.delay:  # read every n-th frame

            if ret:
                # Start capturing here
                if received_frame_id >= self.start_frame_id:
                    frame_id += 1

                    print('[%s] Received frame-%d' % (get_current_time(), frame_id))

                    # Force stop after n frames; disabled when self.max_frames == 0
                    if not self.opt.is_unlimited:
                        if frame_id == (self.max_frames + 1) and self.max_frames > 0:
                            self.is_running = False
                            is_break = True
                            # break

                    self.send_frame_data(frame, frame_id)

                    t0_load_balancer = time.time()
                    self.__load_balancing(frame_id, frame)
                    t_load_bal = time.time() - t0_load_balancer
                    # print("Latency [Load Balancer] of frame-%d: (%.5fs)" % (frame_id, t_load_bal))

            else:
                print("IMAGE is INVALID.")
                print("I guess there is no more frame to show.")
                is_break = True

            n = 0

        print("")
        # print(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")

        return n, frame_id, is_break

    def send_frame_data(self, frame, frame_id):
        # t0_sender = time.time()
        self.frame_sender.send_image(str(frame_id), frame)  # send into PLF component
        self.frame_sender_visualizer.send_image(str(frame_id), frame)  # send into visualizer (original)
        # t_recv = time.time() - t0_sender
        # print('Latency [Send Frame into PLF] of frame-%s: (%.5fs)' % (str(frame_id), t_recv))

        if self.opt.enable_cv_out:
            data = {
                "drone_id": self.opt.drone_id,
                "frame_id": frame_id,
                "visual_type": self.opt.visual_type
            }
            p_mdata = json.dumps(data)
            pub(self.rc_data, self.plf_send_status_channel, p_mdata)  # confirm PLF that frame-n has been sent
            pub(self.rc_data, self.visualizer_channel, p_mdata)  # confirm Visualizer that frame-n has been sent
        # print('\t[PUBLISH Frame-%d into PLF]' % frame_id)
