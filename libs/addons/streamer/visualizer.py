import cv2 as cv
import imagezmq
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.utils import store_fps
import simplejson as json
import time


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
            self.__set_cv_window()
            self.watch_incoming_frames()
        except:
            print("\nUnable to communicate with the Streaming. Restarting . . .")
            cv.destroyAllWindows()

    # Sent by: `pih_location_fetcher_handler.py`
    def watch_incoming_frames(self):
        pub_sub_sender = self.rc_data.pubsub()
        pub_sub_sender.subscribe([self.visualizer_status_channel])

        t0 = None
        for item in pub_sub_sender.listen():
            if isinstance(item["data"], int):
                pass
            else:
                data = self.__extract_json_data(item["data"])

                _, processed_img = self.plotted_img_receiver.recv_image()
                cv.imshow("Image", processed_img)

                # FPS load frame of each worker
                if t0 is None:
                    t0 = data["ts"]
                # frame_id = total_frames
                fps_visualizer_key = "fps-visualizer-%s" % str(data["drone_id"])
                total_frames, current_fps = store_fps(self.rc_latency, fps_visualizer_key, data["drone_id"],
                                                      total_frames=int(data["frame_id"]), t0=t0)
                print('Current [FPS Visualizer of Drone-%d] with total %d frames: (%.2f fps)' % (
                    data["drone_id"], total_frames, current_fps))
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
