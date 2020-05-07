import cv2 as cv
import imagezmq
from libs.addons.redis.translator import redis_get, redis_set, pub
from libs.settings import common_settings
from libs.addons.redis.my_redis import MyRedis
from libs.algorithms.pih_location_fetcher import PIHLocationFetcher
from models import *  # set ONNX_EXPORT in models.py
from utils.datasets import *
import simplejson as json


class Visualizer(MyRedis):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        # self.is_running = True
        self.visualizer_status_channel = "visualizer-status-" + str(self.opt.drone_id)
        print(" #### visualizer_status_channel: ", self.visualizer_status_channel)
        self.__set_visual_receiver()

    # # PiH Location Fetcher (plf)
    # def __set_plf_receiver(self):
    #     url = 'tcp://127.0.0.1:' + str(self.opt.pih_location_fetcher_port)
    #     self.plotted_img_receiver = imagezmq.ImageHub(open_port=url, REQ_REP=False)
    #     # self.plf_receiver_channel = "plf-sender"

    # Visualizer
    # def __set_visual_sender(self):
    #     port = self.opt.visualizer_port_prefix + str(self.drone_id)
    #     url = 'tcp://127.0.0.1:' + port
    #     self.visual_receiver = imagezmq.ImageSender(connect_to=url, REQ_REP=False)

    def __set_visual_receiver(self):
        port = self.opt.visualizer_port_prefix + str(self.opt.drone_id)
        url = 'tcp://127.0.0.1:' + port
        self.plotted_img_receiver = imagezmq.ImageHub(open_port=url, REQ_REP=False)
        # self.viewer_receiver = imagezmq.ImageSender(connect_to=url, REQ_REP=False)

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
            # The following frees up resources and closes all windows
            # self.cap.release()
            cv.destroyAllWindows()
        # while self.is_running:


    # Sent by: `pih_location_fetcher_handler.py`
    def watch_incoming_frames(self):
        pub_sub_sender = self.rc_data.pubsub()
        pub_sub_sender.subscribe([self.visualizer_status_channel])
        for item in pub_sub_sender.listen():
            if isinstance(item["data"], int):
                pass
            else:
                print("\t [FOUND you]")
                _, processed_img = self.plotted_img_receiver.recv_image()
                print("\t ---- COLLECTED Plotted image:", processed_img.shape)
                cv.imshow("Image", processed_img)
                # frame_data = json.loads(item["data"])
                # self.capture_extracted_frame_data(frame_data)
                # print(" --- `Frame Data` has been sent; DATA=", frame_data)
                # self.watch_frame_receiver()

            if cv.waitKey(1000) & 0xFF == ord('q'):
                break
