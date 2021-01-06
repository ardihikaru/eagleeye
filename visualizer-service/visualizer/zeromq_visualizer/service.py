import asab
import logging
from ext_lib.utils import get_imagezmq
from ext_lib.redis.my_redis import MyRedis
import cv2
import time
from ext_lib.utils import get_current_time
import numpy as np

###

L = logging.getLogger(__name__)


###


class ZeroMQVisualizerService(asab.Service):
    """
        A class to publisher (TCP) frames with plotted PiH BBox into a specific port
    """

    def __init__(self, app, service_name="visualizer.ZeroMQVisualizerService"):
        super().__init__(app, service_name)
        self.ImagePlotterService = app.get_service("visualizer.ImagePlotterService")
        self.FPSCalculatorService = app.get_service("visualizer.FPSCalculatorService")
        # self.ZMQService = app.get_service("visualizer.ZMQService")

        self.redis = MyRedis(asab.Config)
        self._mode = asab.Config["stream:config"]["mode"]
        self._t0_streaming = None  # set variable to calculate FPS

        self._is_resized = bool(int(asab.Config["stream:out"]["is_resized"]))
        self._is_encoded = asab.Config["stream:out"].getboolean("is_encoded")
        self._encode_size = asab.Config["stream:out"].getint("encode_size")
        self._out_width = int(asab.Config["stream:out"]["width"])
        self._out_height = int(asab.Config["stream:out"]["height"])

    async def run(self, zmq_receiver, zmq_publisher):
        is_latest_plot_available = False
        while True:
            try:
                is_success, frame_id, t0_zmq, img = get_imagezmq(zmq_receiver)

                # Set initial value
                if await self.FPSCalculatorService.get_start_time() is None:
                    await self.FPSCalculatorService.start()

                t1_zmq = (time.time() - t0_zmq) * 1000
                if is_success:
                    fps = await self.FPSCalculatorService.get_fps(frame_id)
                    L.warning('Latency [Visualizer Capture] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
                    is_latest_plot_available = await self.ImagePlotterService.plot_img(is_latest_plot_available,
                                                                                       frame_id, img, fps)

                    # start publishing frames
                    self.publish_image(zmq_publisher, frame_id, img)
                    # L.warning('*** Current FPS: {}'.format(await self.FPSCalculatorService.get_fps(frame_id)))
            except Exception as e:
                print("No more frame to show; Reason: {}".format(e))
                break

    def publish_image(self, zmq_sender, frame_id, frame):
        t0_zmq = time.time()
        zmq_id = str(frame_id) + "-" + str(t0_zmq)

        # resize the frame; Default VGA (640 x 480)
        if self._is_resized:
            frame = cv2.resize(frame, (self._out_width, self._out_height))

        # compress the frame to reduce bandwidth usage
        if self._is_encoded:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self._encode_size]
            _, encoded_img = cv2.imencode('.jpg', frame, encode_param)
            frame = encoded_img

        zmq_sender.send_image(zmq_id, frame)
        t1_zmq = (time.time() - t0_zmq) * 1000
        L.warning('Latency [Publish Image via ZeroMQ] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
        # TODO: Saving latency for scheduler:latency:sending_image_zmq

