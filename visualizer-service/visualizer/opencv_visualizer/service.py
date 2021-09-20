import asab
import logging
from ext_lib.utils import get_imagezmq
from ext_lib.redis.my_redis import MyRedis
import cv2
import time
from ext_lib.utils import get_current_time
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class OpenCVVisualizerService(asab.Service):
    """
        A class to visualize a realtime object detection with plotted PiH BBox
    """

    def __init__(self, app, service_name="visualizer.OpenCVVisualizerService"):
        super().__init__(app, service_name)
        self.ImagePlotterService = app.get_service("visualizer.ImagePlotterService")
        self.FPSCalculatorService = app.get_service("visualizer.FPSCalculatorService")

        self.redis = MyRedis(asab.Config)
        self._mode = asab.Config["stream:config"]["mode"]
        self._window_title = asab.Config["stream:config"]["path"]
        self._window_width = int(asab.Config["stream:config"]["window_width"])
        self._window_height = int(asab.Config["stream:config"]["window_height"])
        self._t0_streaming = None  # set variable to calculate FPS

        self.compressed_img = asab.Config["image:preprocessing"].getboolean("compressed_img")

    async def run(self, zmq_receiver):
        cv2.namedWindow(self._window_title, cv2.WND_PROP_FULLSCREEN)
        cv2.resizeWindow(self._window_title, self._window_width, self._window_height)  # Enter your size

        is_latest_plot_available = False
        while True:
            try:
                is_success, frame_id, t0_zmq, raw_img = get_imagezmq(zmq_receiver)

                # try to decompress the captured image (depends on the config)
                t0_decompress_in_subprocess = time.time()
                if self.compressed_img:
                    # captured image is compressed, try to decompress
                    t0_decompress_in_subprocess = time.time()
                    deimg_len = list(raw_img.shape)[0]
                    decoded_img = raw_img.reshape(deimg_len, 1)
                    decompressed_img = cv2.imdecode(decoded_img, 1)  # decompress
                    img = decompressed_img.copy()
                else:
                    img = raw_img.copy()
                t1_decompress_in_subprocess = (time.time() - t0_decompress_in_subprocess) * 1000
                L.log(LOG_NOTICE, '[{}] Proc. Latency of %s for frame-%s (%.3f ms)'.format(get_current_time()) % (
                    "DECOMPRESS-IN-DETECTION-SERVICE", str(frame_id), t1_decompress_in_subprocess))

                # Set initial value
                if await self.FPSCalculatorService.get_start_time() is None:
                    await self.FPSCalculatorService.start()

                t1_zmq = (time.time() - t0_zmq) * 1000
                if is_success:
                    fps = await self.FPSCalculatorService.get_fps(frame_id)
                    L.log(LOG_NOTICE, 'Latency [Visualizer Capture] of frame-{}: (%.5fms)'.format(str(frame_id))
                          % t1_zmq)
                    is_latest_plot_available = await self.ImagePlotterService.plot_img(is_latest_plot_available,
                                                                                       frame_id, img, fps)
                    cv2.imshow(self._window_title, img)
            except Exception as e:
                L.error("No more frame to show; Reason: {}".format(e))
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # The following frees up resources and closes all windows
        cv2.destroyAllWindows()
