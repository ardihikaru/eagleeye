import cv2 as cv
import imagezmq
from libs.addons.redis.translator import redis_get, redis_set
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.utils import store_fps, get_gps_data
import simplejson as json
import time
from datetime import datetime
from utils.utils import plot_gps_info, plot_fps_info
from imutils.video import FileVideoStream


class Visualizer(MyRedis):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        self.visualizer_status_channel = "visualizer-status-" + str(self.opt.drone_id)
        self.visualizer_origin_channel = "visualizer-origin-" + str(self.opt.drone_id)
        self.__set_visual_receiver()

    def __set_visual_receiver(self):
        # frame + obj. detection
        port = self.opt.visualizer_port_prefix + str(self.opt.drone_id)
        url = 'tcp://127.0.0.1:' + port
        self.plotted_img_receiver = imagezmq.ImageHub(open_port=url, REQ_REP=False)

        # original frame
        port = self.opt.visualizer_port_prefix + "0"
        url = 'tcp://127.0.0.1:' + port
        self.original_img_receiver = imagezmq.ImageHub(open_port=url, REQ_REP=False)

    def __set_window_position(self, is_obj_det):
        x, y = 0, 0
        if self.opt.small:
            x = int(self.opt.window_width / 2) + 40
            if is_obj_det:
                y = int(self.opt.window_width / 4) + 80
        cv.moveWindow("Image", x, y)

    def __set_window_size(self):
        width = self.opt.window_width
        height = self.opt.window_height
        ignored_width = 40
        ignored_height = 40
        if self.opt.small:
            width = int(width / 2) - ignored_width
            height = int(height / 2) - ignored_height
        cv.resizeWindow("Image", width, height)

    def __set_cv_window(self, is_obj_det, window_name):
        cv.namedWindow(window_name, cv.WND_PROP_FULLSCREEN)
        cv.moveWindow(window_name, 0, 0)
        self.__set_window_position(is_obj_det)
        # cv.resizeWindow("Image", self.opt.window_width, self.opt.window_height)
        self.__set_window_size()

    def run(self):
        print("\nMonitoring realtime object detection:")
        try:
            if self.opt.original:
                self.waiting_for_action()
                # self.watch_incoming_frames(self.visualizer_origin_channel)
            else:
                self.watch_incoming_frames(self.visualizer_status_channel, is_obj_det=True)
        except Exception as e:
            # print(" -- ERROR:", e)
            print("\nUnable to communicate with the Streaming. Restarting . . .")
            cv.destroyAllWindows()

    def waiting_for_action(self):
        channel = "stream-origin"
        pub_sub_sender = self.rc_data.pubsub()
        pub_sub_sender.subscribe([channel])
        for item in pub_sub_sender.listen():
            if isinstance(item["data"], int):
                pass
            else:
                # TO DO here
                data = self.__extract_json_data(item["data"])
                self.streaming_with_raw_frames(data)
                break

    def streaming_with_raw_frames(self, data):
        window_name = "Original_Stream"
        self.__set_cv_window(False, window_name)
        # loop over frames from the video file stream
        fvs = FileVideoStream(data["source"]).start()
        while fvs.more():
            try:
                # grab the frame from the threaded video file stream, resize
                # it, and convert it to grayscale (while still retaining 3 channels)
                frame = fvs.read()

                # # add gps information
                # img_height, img_width, _ = frame.shape
                # gps_data = get_gps_data(self.rc_gps, data["source"])
                #
                # if self.opt.show_fps:
                #     img = plot_fps_info(img_width, data["drone_id"], data["frame_id"], self.rc_latency, frame,
                #                         redis_set, redis_get)
                # plot_gps_info(img_height, gps_data, "-", frame)

                # show the frame and update the FPS counter
                cv.imshow(window_name, frame)
                cv.waitKey(1)
            except Exception as e:
                print("error: ", e)
                pass
        # do a bit of cleanup
        cv.destroyAllWindows()
        fvs.stop()

    # Sent by: `pih_location_fetcher_handler.py`
    def watch_incoming_frames(self, channel, is_obj_det=False):
        window_name = "EagleEYE_Stream"
        pub_sub_sender = self.rc_data.pubsub()
        pub_sub_sender.subscribe([channel])

        is_start = False
        # t0 = None
        # t0 = time.time()
        for item in pub_sub_sender.listen():
            if isinstance(item["data"], int):
                pass
            else:
                if not is_start:
                    is_start = True
                    # t0 = time.time()
                    self.__set_cv_window(is_obj_det, window_name)

                data = self.__extract_json_data(item["data"])

                if is_obj_det:
                    _, img = self.plotted_img_receiver.recv_image()
                    # _, processed_img = self.plotted_img_receiver.recv_image()
                else:
                    _, img = self.original_img_receiver.recv_image()
                    img_height, img_width, _ = img.shape
                    gps_data = get_gps_data(self.rc_gps, data["drone_id"])

                    if self.opt.show_fps:
                        img = plot_fps_info(img_width, data["drone_id"], data["frame_id"], self.rc_latency, img,
                                            redis_set, redis_get)
                    plot_gps_info(img_height, gps_data, "-", img)

                # cv.imshow("Image", processed_img)
                cv.imshow(window_name, img)

                # FPS load frame of each worker
                # if t0 is None:
                #     t0 = data["ts"]
                # frame_id = total_frames
                # fps_visualizer_key = "fps-visualizer-%s" % str(data["drone_id"])
                # total_frames, current_fps = store_fps(self.rc_latency, fps_visualizer_key, data["drone_id"],
                #                                       total_frames=int(data["frame_id"]), t0=t0)

                # t0_frame_key = "t0-frame-" + str(data["drone_id"]) + "-" + str(data["frame_id"])
                # print(" --- t0_frame_key: ", t0_frame_key)
                # t0 = redis_get(self.rc_latency, t0_frame_key)
                #
                # t1 = time.time()
                # current_fps = 1.0 / (t1 - t0)

                frame_time = datetime.now().strftime("%H:%M:%S")
                print("\n[%s] Received frame-%d" % (frame_time, int(data["frame_id"])))
                # print('Current [FPS Visualizer of Drone-%d] with total %d frames: (%.2f fps)' % (
                #     data["drone_id"], total_frames, current_fps))
                # print('Current [FPS Visualizer of Drone-%d] for frame-%s: (%.2f fps)' % (
                #     data["drone_id"], str(data["frame_id"]), current_fps))
                # print('Latency [Visualize frame] of frame-%s: (%.5fs)' % (str(data["frame_id"]), current_fps))

            # if cv.waitKey(1) & 0xFF == ord('q'):
            if cv.waitKey(self.opt.wait_key) & 0xFF == ord('q'):
                break

    def __extract_json_data(self, json_data):
        data = None
        try:
            data = json.loads(json_data)
        except:
            pass
        return data
