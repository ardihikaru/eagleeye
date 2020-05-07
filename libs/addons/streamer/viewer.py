import cv2 as cv
import imagezmq
from libs.addons.redis.translator import redis_get, redis_set, pub
from libs.settings import common_settings
from libs.addons.redis.my_redis import MyRedis
from libs.algorithms.pih_location_fetcher import PIHLocationFetcher
from models import *  # set ONNX_EXPORT in models.py
from utils.datasets import *
import simplejson as json


class Viewer:
    def __init__(self, opt):
        self.opt = opt
        self.is_running = True
        self.__set_viewer_receiver()

    def __set_viewer_receiver(self):
        url = 'tcp://127.0.0.1:' + str(self.opt.viewer_port)
        self.viewer_receiver = imagezmq.ImageSender(connect_to=url, REQ_REP=False)

    def run(self):
        print("\nMonitoring realtime object detection:")
        while self.is_running:
            try:
                # self.cap = cv.VideoCapture(self.opt.source)
                self.__set_cv_window()
                # self.__start_streaming()
            except:
                print("\nUnable to communicate with the Streaming. Restarting . . .")
                # The following frees up resources and closes all windows
                # self.cap.release()
                if self.opt.enable_cv_out:
                    cv.destroyAllWindows()

    def __set_cv_window(self):
        if self.opt.enable_cv_out:
            cv.namedWindow("Image", cv.WND_PROP_FULLSCREEN)
            cv.moveWindow("Image", 0, 0)
            cv.resizeWindow("Image", self.opt.viewer_width, self.opt.viewer_height)  # Enter your size
