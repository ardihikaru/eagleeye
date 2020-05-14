import cv2 as cv
import imagezmq
from libs.addons.redis.translator import redis_get
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.utils import store_fps
import simplejson as json
import time
from datetime import datetime


class Visualizer(MyRedis):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        self.visualizer_status_channel = "visualizer-status-" + str(self.opt.drone_id)
        self.__set_visual_receiver()

    def __set_visual_receiver(self):
        port = self.opt.visualizer_port_prefix + str(self.opt.drone_id)
        url = 'tcp://127.0.0.1:' + port
        self.plotted_img_receiver = imagezmq.ImageHub(open_port=url, REQ_REP=False)

    def __set_cv_window(self):
        cv.namedWindow("Image", cv.WND_PROP_FULLSCREEN)
        cv.moveWindow("Image", 0, 0)
        cv.resizeWindow("Image", self.opt.window_width, self.opt.window_height)

    def run(self):
        print("\nMonitoring realtime object detection:")
        try:
            # self.__set_cv_window()
            self.watch_incoming_frames()
        except:
            print("\nUnable to communicate with the Streaming. Restarting . . .")
            cv.destroyAllWindows()

    # Sent by: `pih_location_fetcher_handler.py`
    def watch_incoming_frames(self):
        pub_sub_sender = self.rc_data.pubsub()
        pub_sub_sender.subscribe([self.visualizer_status_channel])

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
                    self.__set_cv_window()

                data = self.__extract_json_data(item["data"])

                _, processed_img = self.plotted_img_receiver.recv_image()
                cv.imshow("Image", processed_img)

                # FPS load frame of each worker
                # if t0 is None:
                #     t0 = data["ts"]
                # frame_id = total_frames
                # fps_visualizer_key = "fps-visualizer-%s" % str(data["drone_id"])
                # total_frames, current_fps = store_fps(self.rc_latency, fps_visualizer_key, data["drone_id"],
                #                                       total_frames=int(data["frame_id"]), t0=t0)

                t0_frame_key = "t0-frame-" + str(data["drone_id"]) + "-" + str(data["frame_id"])
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
