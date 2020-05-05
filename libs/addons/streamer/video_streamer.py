import cv2 as cv
from redis import StrictRedis
import time
import imagezmq
from multiprocessing import Process
from libs.addons.redis.translator import frame_producer, redis_get, redis_set, pub
from libs.settings import common_settings
# from libs.addons.streamer.realtime_viewer import RealtimeViewer
from libs.algorithms.pih_location_fetcher import PIHLocationFetcher
from utils.utils import *
from models import *  # set ONNX_EXPORT in models.py
from utils.datasets import *
import simplejson as json


class VideoStreamer:
    def __init__(self, opt):
        # print(" -------- @ VideoStreamer")
        self.opt = opt
        self.save_path = opt.output_folder
        self.__set_redis()

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

        self.worker_id = 0 # reset, when total workers = `self.opt.total_workers`

        # Empty folders
        out_folder = opt.output_folder + str(opt.drone_id)
        if os.path.exists(out_folder):
            shutil.rmtree(out_folder)  # delete output folder
        os.makedirs(out_folder)  # make new output folder

        # self.sender_w1 = imagezmq.ImageSender(connect_to='tcp://127.0.0.1:5553', REQ_REP=False)
        # self.sender_w1 = imagezmq.ImageSender(connect_to='tcp://127.0.0.1:5555', REQ_REP=False)
        # self.channel_zmq = "pub-image"
        self.zmq_sender = []

        self.__set_zmq_senders()

    def __set_zmq_senders(self):
        for i in range(int(self.opt.total_workers)):
            url = 'tcp://127.0.0.1:555' + str((i+1))
            sender = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
            self.zmq_sender.append(sender)

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
        if self.opt.source_type == "folder":
            print("\nReading folder:")
            t_stream_setup_key = "stream-start-" + str(self.opt.drone_id)
            redis_set(self.rc_latency, t_stream_setup_key, time.time())
            self.detect_from_folder()

        else:
            print("\nReading video:")
            # while True:
            while self.is_running:
                try:
                    # t0_stream_setup = time.time()
                    self.cap = cv.VideoCapture(self.opt.source)
                    # t_stream_setup = time.time() - t0_stream_setup
                    # t_stream_setup_key = "stream-setup-" + str(self.opt.drone_id)
                    # t_stream_setup_key = "stream-start-" + str(self.opt.drone_id)
                    # redis_set(self.rc_latency, t_stream_setup_key, time.time())

                    # Latency:
                    # t_stream_setup_key = "stream-setup-" + str(self.opt.drone_id)
                    # redis_set(self.rc_latency, t_stream_setup_key, t_stream_setup)
                    # print('\nLatency [Stream Setup Time]: (%.5fs)' % (t_stream_setup))

                    if self.opt.enable_cv_out:
                        cv.namedWindow("Image", cv.WND_PROP_FULLSCREEN)
                        cv.resizeWindow("Image", 1366, 768)  # Enter your size

                    self.__start_streaming()
                except:
                    # if not self.opt.auto_restart:
                    #     print("\nUnable to communicate with the Streaming. Stopping the system. . .")
                    #     self.is_running = False
                    # else:
                    #     print("\nUnable to communicate with the Streaming. Restarting . . .")
                    print("\nUnable to communicate with the Streaming. Restarting . . .")
                    # time.sleep(1) # Delay 1 second before trying again
                    # The following frees up resources and closes all windows
                    self.cap.release()
                    if self.opt.enable_cv_out:
                        cv.destroyAllWindows()

    def detect_from_folder(self):
        n = 0
        frame_id = 0
        received_frame_id = 0

        # Set Dataloader
        # vid_path, vid_writer = None, None
        # save_img = True
        dataset = LoadImages(self.opt.source, img_size=self.opt.img_size, half=self.opt.half)

        # Save timestamp to start extracting video streaming.
        t_start_key = "start-" + str(self.opt.drone_id)
        redis_set(self.rc_latency, t_start_key, time.time())

        # urutkan index
        dataset_idx = []
        for i in range(57):
            dataset_idx.append([])

        i = 0
        for path, img, im0s, vid_cap in dataset:
            real_frame_idx = int((path.replace("data/5g-dive/57-frames/out", "")).replace(".png", ""))
            real_idx = real_frame_idx - 1
            print(" >>> Re-arranging real_idx: ", real_idx)
            dataset_idx[real_idx] = [path, img, im0s, vid_cap]
            i += 1

        # print("dataset_idx:", type(dataset))
        # print("\n\ndataset_idx:", len(dataset_idx))
        # print("dataset_idx[0]:", dataset_idx[0])

        # for path, img, im0s, vid_cap in dataset:
        for i in range(len(dataset_idx)):
            received_frame_id, path, img, im0s, vid_cap = (i+1), dataset_idx[i][0], dataset_idx[i][1], \
                                                          dataset_idx[i][2], dataset_idx[i][3]
            # received_frame_id += 1
            # received_frame_id = int((path.replace("data/5g-dive/57-frames/out", "")).replace(".png", ""))

            t_sframe_key = "start-fi-" + str(self.opt.drone_id)  # to calculate end2end latency each frame.
            redis_set(self.rc_latency, t_sframe_key, time.time())

            n += 1

            t0_frame = time.time()
            # ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
            try:
                # ret, frame = self.cap.read()
                # ret, frame = True, img
                ret, frame = True, im0s

                # Latency: capture each frame
                t_frame = time.time() - t0_frame
                print('\nLatency [Reading stream frame] of frame-%d: (%.5fs)' % (received_frame_id, t_frame))
                t_frame_key = "frame-" + str(self.opt.drone_id) + "-" + str(frame_id)
                redis_set(self.rc_latency, t_frame_key, t_frame)

                if n == self.opt.delay:  # read every n-th frame

                    if ret:
                        # Start capturing here
                        if received_frame_id >= self.start_frame_id:
                            frame_id += 1

                            # Force stop after n frames
                            # if frame_id > int(self.max_frames):
                            if frame_id == (self.max_frames + 1) and self.max_frames > 0:
                                self.is_running = False
                                break

                            save_path = self.opt.output_folder + str(self.opt.drone_id) + "/frame-%d.jpg" % frame_id
                            mbbox_path = self.opt.mbbox_output + str(self.opt.drone_id) + "/frame-%d.jpg" % frame_id
                            bbox_path = self.opt.normal_output + "/frame-%d.jpg" % frame_id

                            # self.__load_balancing(frame_id, ret, frame, save_path)
                            self.__load_balancing(frame_id, frame)

                            if self.opt.enable_cv_out:
                                if self.opt.enable_mbbox:
                                    # time.sleep(0.2)
                                    # if os.path.isfile(mbbox_path):
                                    #     print("--------File exist")
                                    # else:
                                    #     print("--------File not exist")

                                    # while not os.path.isfile(mbbox_path):
                                    while not os.path.isfile(bbox_path):
                                        time.sleep(0.01)
                                        # time.sleep(0.5)
                                        continue
                                    time.sleep(0.05)
                                    # img = np.asarray(cv2.imread(mbbox_path))
                                    img = np.asarray(cv2.imread(bbox_path))
                                    cv.imshow("Image", img)
                                else:
                                    cv.imshow("Image", frame)

                    else:
                        print("IMAGE is INVALID.")
                        print("I guess there is no more frame to show.")
                        break

                    n = 0
                # time.sleep(0.01)  # wait time

            except Exception as e:
                print(" ---- e:", e)
                if not self.opt.auto_restart:
                    print("\nStopping the system. . .")
                    time.sleep(7)
                    self.is_running = False
                else:
                    print("No more frame to show.")
                break

            if cv.waitKey(10) & 0xFF == ord('q'):
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

    # def __load_balancing(self, frame_id, ret, frame, save_path):
    def __load_balancing(self, frame_id, frame):
        # Initially, send process into first worker
        self.worker_id += 1
        stream_channel = common_settings["redis_config"]["channel_prefix"] + str(self.worker_id)

        # Check worker status first, please wait while still working
        # print(">>>>>> __worker_status = ", self.__worker_status())
        w = 0
        wait_time = self.wait_time
        if redis_get(self.rc_data, self.worker_id) is None:
            print("This worker is OFF. Nothing to do")
            print("TBD next time: Should skip this worker and move to the next worker instead")
            self.__find_optimal_worker()
        else:
            # None = DISABLED; 1=Ready; 0=Busy
            while self.__worker_status() == 0:
                # print("\nWorker-%d is still processing other image, waiting (%ds) ..." % (self.worker_id, w))
                # print("\nWorker-%d is still processing other image, waiting ... " % self.worker_id)
                # time.sleep(0.005)
                if not self.opt.disable_delay:
                    time.sleep(self.wait_time)
                w += self.wait_time

            # # Send multi-process and set the worker as busy (value=False)
            # print("### Sending the work into [worker-#%d] @ `%s`" % (self.worker_id, stream_channel))
            # Process(target=frame_producer, args=(self.rc, frame_id, ret, frame, save_path, stream_channel,
            #                                      self.rc_latency, self.opt.drone_id, self.worker_id)).start()

            data = {
                "frame_id": frame_id,
                "worker_id": self.worker_id
                # "img_path": save_path
            }
            p_mdata = json.dumps(data)

            # Configure ZMQ & Redis Pub/Sub parameters
            # print(" @ Configure ZMQ & Redis Pub/Sub parameters")
            # Send frame into ZMQ channel
            ts = time.time()
            # self.sender_w1.send_image(str(frame_id), frame)
            zid = self.worker_id - 1

            self.zmq_sender[zid].send_image(str(frame_id), frame)
            t_recv = time.time() - ts
            print('\nLatency [Send imagezmq] of frame-%s: (%.5fs)' % (str(frame_id), t_recv))
            # pub(self.rc_data, self.channel_zmq, ts)

            # Latency: capture publish frame information
            t0_pub2frame = time.time()
            pub(self.rc_data, stream_channel, p_mdata)
            t_pub2frame = time.time() - t0_pub2frame
            print('\nLatency [Publish frame info] of frame-%s: (%.5fs)' % (str(frame_id), t_pub2frame))
            t_pub2frame_key = "pub2frame-" + str(self.opt.drone_id) + "-" + str(frame_id)
            redis_set(self.rc_data, t_pub2frame_key, t_pub2frame)

            # print(" ### FINISHED ### PUBLISHING ...")
            # print(".. [Worker-%d][time=%s] Sending image (1920 x 1080) in (%.5fs)." % (self.worker_id, str(ts), t_recv))
            # ENDED

            redis_set(self.rc_data, self.worker_id, 0)

        self.__reset_worker()

    def __start_streaming(self):
        n = 0
        frame_id = 0
        received_frame_id = 0
        # t_start = time.time()
        # redis_set(self.rc_latency, "start", t_start)

        # Save timestamp to start extracting video streaming.
        t_start_key = "start-" + str(self.opt.drone_id)
        redis_set(self.rc_latency, t_start_key, time.time())

        # while (self.cap.isOpened()):
        while (self.cap.isOpened()) and self.is_running:
            received_frame_id += 1

            t_sframe_key = "start-fi-" + str(self.opt.drone_id) # to calculate end2end latency each frame.
            redis_set(self.rc_latency, t_sframe_key, time.time())
            n += 1
            t0_frame = time.time()

            # ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
            try:
                ret, frame = self.cap.read()

                # Latency: capture each frame
                t_frame = time.time() - t0_frame
                print('\nLatency [Reading stream frame] of frame-%d: (%.5fs)' % (received_frame_id, t_frame))
                t_frame_key = "frame-" + str(self.opt.drone_id) + "-" + str(frame_id)
                redis_set(self.rc_latency, t_frame_key, t_frame)

                if n == self.opt.delay:  # read every n-th frame

                    if ret:
                        # Start capturing here
                        if received_frame_id >= self.start_frame_id:
                            frame_id += 1

                            # Force stop after n frames; disabled when self.max_frames == 0
                            if frame_id == (self.max_frames + 1) and self.max_frames > 0:
                                self.is_running = False
                                break

                            self.__load_balancing(frame_id, frame)

                            if self.opt.enable_cv_out:
                                processed_img = self.__get_img_data(frame, frame_id)
                                cv.imshow("Image", processed_img)

                    else:
                        print("IMAGE is INVALID.")
                        print("I guess there is no more frame to show.")
                        break

                    n = 0
                # time.sleep(0.01)  # wait time

            except Exception as e:
                # print(" ---- e:", e)
                if not self.opt.auto_restart:
                    print("\nStopping the system. . .")
                    time.sleep(7)
                    self.is_running = False
                else:
                    print("No more frame to show.")
                break

            if cv.waitKey(100) & 0xFF == ord('q'):
                break

    def __get_img_data(self, raw_frame, frame_id):
        if self.opt.viewer_version == 1:
            return self.__viewer_v1(raw_frame, frame_id)
        elif self.opt.viewer_version == 2:
            return self.__viewer_v2(raw_frame, frame_id)
        else:
            return raw_frame

    # Show real-time image result (EagleEYE v1: EuCNC Conference 2019)
    def __viewer_v1(self, raw_frame, frame_id):
        bbox_path = self.opt.normal_output + "frame-%d.jpg" % frame_id
        if self.opt.enable_mbbox:  # Image with MBBox
            while not os.path.isfile(bbox_path):
                time.sleep(0.01)
                # time.sleep(0.5)
                continue
            time.sleep(0.05)
            img = np.asarray(cv2.imread(bbox_path))
            return img
        else:  # Image with BBox (from YOLOv3 only)
            return raw_frame

    # Show real-time image result (EagleEYE v2: GLOBECOM Conference 2020)
    def __viewer_v2(self, raw_frame, frame_id):
        pih_gen = PIHLocationFetcher(self.opt, raw_frame, frame_id)
        pih_gen.run()
        return pih_gen.get_mbbox_img()
