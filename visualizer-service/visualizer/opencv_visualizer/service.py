import asab
import logging
from ext_lib.utils import get_imagezmq
from ext_lib.redis.my_redis import MyRedis
import cv2
import time
from ext_lib.utils import get_current_time

###

L = logging.getLogger(__name__)


###


class OpenCVVisualizerService(asab.Service):
    """
        A class to visualize a realtime object detection with plotted PiH BBox
    """

    def __init__(self, app, service_name="visualizer.OpenCVVisualizerService"):
        super().__init__(app, service_name)
        self.redis = MyRedis(asab.Config)
        self._mode = asab.Config["stream:config"]["mode"]
        self._window_title = asab.Config["stream:config"]["path"]
        self._window_width = int(asab.Config["stream:config"]["window_width"])
        self._window_height = int(asab.Config["stream:config"]["window_height"])

    async def run(self, zmq_receiver):
        cv2.namedWindow(self._window_title, cv2.WND_PROP_FULLSCREEN)
        cv2.resizeWindow(self._window_title, self._window_width, self._window_height)  # Enter your size
        while True:
            try:
                is_success, frame_id, t0_zmq, img = get_imagezmq(zmq_receiver)
                t1_zmq = (time.time() - t0_zmq) * 1000
                if is_success:
                    L.warning('Latency [Visualizer Capture] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
                    # print(" IMAGE **** {} -- Shape={}".format(frame_id, img.shape))
                    cv2.imshow(self._window_title, img)
            except:
                print("No more frame to show.")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # The following frees up resources and closes all windows
        cv2.destroyAllWindows()
