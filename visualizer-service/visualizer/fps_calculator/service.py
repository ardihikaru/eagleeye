import asab
import logging
from ext_lib.redis.my_redis import MyRedis
import cv2
from datetime import datetime
from ext_lib.utils import get_current_time

###

L = logging.getLogger(__name__)


###


class FPSCalculatorService(asab.Service):
    """
        A class to visualize a realtime object detection with plotted PiH BBox
    """

    def __init__(self, app, service_name="visualizer.FPSCalculatorService"):
        super().__init__(app, service_name)
        self.redis = MyRedis(asab.Config)
        self._start_time = None  # a variable to initiate start time of the FPS calculation

    async def start(self):
        self._start_time = datetime.now()

    async def get_start_time(self):
        return self._start_time

    async def _get_elapsed_time(self):
        end = datetime.now()
        return (end - self._start_time).total_seconds()

    async def get_fps(self, num_frames):
        fps = num_frames / await self._get_elapsed_time()
        return round(fps, 2)
