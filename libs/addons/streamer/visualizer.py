import cv2 as cv
import imagezmq
from libs.addons.redis.my_redis import MyRedis


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
        for item in pub_sub_sender.listen():
            if isinstance(item["data"], int):
                pass
            else:
                _, processed_img = self.plotted_img_receiver.recv_image()
                cv.imshow("Image", processed_img)

            if cv.waitKey(1000) & 0xFF == ord('q'):
                break
