import asab
import logging
import imagezmq
import time
from ext_lib.commons.util import plot_one_box
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_get, redis_set

###

L = logging.getLogger(__name__)


###


class ZMQService(asab.Service):
    """
        A class to receive and send image data (numpy) through ZeroMQ protocol
    """

    def __init__(self, app, service_name="visualizer.ZMQService"):
        super().__init__(app, service_name)
        self.ImagePlotterService = app.get_service("visualizer.ImagePlotterService")

        self.zmq_receiver = None
        self.redis = MyRedis(asab.Config)

    async def set_configurations(self):
        uri = "tcp://%s:%s" % (asab.Config["zmq"]["sender_host"], asab.Config["zmq"]["sender_port"])
        L.warning("[IMPORTANT] Accepted ZMQ URI: %s" % uri)
        self.zmq_receiver = imagezmq.ImageHub(open_port=uri, REQ_REP=False)

    def get_zmq_receiver(self):
        return self.zmq_receiver

    async def _set_zmq_configurations(self):
        await self.set_configurations()

    def _get_imagezmq(self):
        try:
            array_name, image = self.get_zmq_receiver().recv_image()
            tmp = array_name.split("-")
            frame_id = int(tmp[0])
            t0 = float(tmp[1])
            return True, frame_id, t0, image

        except Exception as e:
            L.error("[ERROR]: %s" % str(e))
            return False, None, None, None

    async def start(self):
        await self._set_zmq_configurations()
        L.warning("I am running ...")
        is_latest_plot_available = False
        while True:
            is_success, frame_id, t0_zmq, img = self._get_imagezmq()
            t1_zmq = (time.time() - t0_zmq) * 1000
            if is_success:
                # L.warning('Latency [Visualizer Capture] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
                is_latest_plot_available = await self.ImagePlotterService.plot_img(is_latest_plot_available, frame_id, img)

