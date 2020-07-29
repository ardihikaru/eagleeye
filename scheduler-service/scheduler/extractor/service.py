import asyncio
import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time, pubsub_to_json
import time
from imutils.video import FileVideoStream
import cv2

###

L = logging.getLogger(__name__)


###


class ExtractorService(asab.Service):
    """
        A class to extract either: Video stream or tuple of images
    """

    def __init__(self, app, service_name="scheduler.ExtractorService"):
        super().__init__(app, service_name)

        # start pub/sub
        self.redis = MyRedis(asab.Config)
        # self._run()

        # params for extractor
        self.cap = None
        self.frame_id = 0

    async def extract_folder(self, config):
        print("#### I am extractor FODLER function from ExtractorService!")
        print(config)

    async def extract_video_stream(self, config):
        print("#### I am extractor VIDEO STREAM function from ExtractorService!")
        print(config)
        try:
            self.cap = await self._set_cap(config)

            while await self._streaming():
                self.frame_id += 1
                success, frame = await self._read_frame()
                print(" --- success:", self.frame_id, success, frame.shape)
        except Exception as e:
            print(" ---- >> e:", e)

    async def _set_cap(self, config):
        if bool(asab.Config["stream:config"]["thread"]):
            return FileVideoStream(config["uri"]).start()  # Thread-based video capture
        else:
            return cv2.VideoCapture(config["uri"])

    async def _streaming(self):
        if bool(asab.Config["stream:config"]["thread"]):
            return self.cap.more()
        else:
            return True

    async def _read_frame(self):
        if bool(asab.Config["stream:config"]["thread"]):
            return True, self.cap.read()
        else:
            return self.cap.read()
