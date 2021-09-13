import asab
import logging
from asab import LOG_NOTICE
from ext_lib.utils import get_imagezmq
from ext_lib.redis.my_redis import MyRedis
import cv2
import time
from ext_lib.utils import get_current_time

###

L = logging.getLogger(__name__)


###


class RTSPVisualizerService(asab.Service):
    """
        A class to visualize a realtime object detection with plotted PiH BBox
    """

    def __init__(self, app, service_name="visualizer.RTSPVisualizerService"):
        super().__init__(app, service_name)
        self.ImagePlotterService = app.get_service("visualizer.ImagePlotterService")
        self.FPSCalculatorService = app.get_service("visualizer.FPSCalculatorService")

        self.redis = MyRedis(asab.Config)
        self._mode = asab.Config["stream:config"]["mode"]
        self._window_title = asab.Config["stream:config"]["path"]
        self._window_width = int(asab.Config["stream:config"]["window_width"])
        self._window_height = int(asab.Config["stream:config"]["window_height"])

    async def run(self, zmq_receiver):
        is_latest_plot_available = False

        while True:
            is_success, frame_id, t0_zmq, img = get_imagezmq(zmq_receiver)
            # t1_zmq = (time.time() - t0_zmq) * 1000

            t1_zmq = (time.time() - t0_zmq) * 1000
            if is_success:

                # Set initial value
                if await self.FPSCalculatorService.get_start_time() is None:
                    await self.FPSCalculatorService.start()

                # get the current FPS
                fps = await self.FPSCalculatorService.get_fps(frame_id)
                L.log(LOG_NOTICE, '[RTSP] Latency [Visualizer Capture] of frame-{}: (%.5fms)'.format(str(frame_id))
                      % t1_zmq)

                is_latest_plot_available = await self.ImagePlotterService.plot_img(is_latest_plot_available, frame_id,
                                                                                   img, fps)
