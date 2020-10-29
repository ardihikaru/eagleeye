import asab
import logging
import imagezmq
from ext_lib.utils import get_imagezmq

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
        self.OpenCVVisualizerService = app.get_service("visualizer.OpenCVVisualizerService")
        self.RTSPVisualizerService = app.get_service("visualizer.RTSPVisualizerService")

        self.zmq_receiver = None
        self._mode = asab.Config["stream:config"]["mode"]

    async def set_configurations(self):
        uri = "tcp://%s:%s" % (asab.Config["zmq"]["sender_host"], asab.Config["zmq"]["sender_port"])
        L.warning("[IMPORTANT] Accepted ZMQ URI: %s" % uri)
        self.zmq_receiver = imagezmq.ImageHub(open_port=uri, REQ_REP=False)

    def get_zmq_receiver(self):
        return self.zmq_receiver

    async def _set_zmq_configurations(self):
        await self.set_configurations()

    async def start(self):
        await self._set_zmq_configurations()
        L.warning("I am running ...")
        is_latest_plot_available = False

        if self._mode == "opencv":
            await self.OpenCVVisualizerService.run(self.get_zmq_receiver())
        else:
            await self.RTSPVisualizerService.run(self.get_zmq_receiver())
