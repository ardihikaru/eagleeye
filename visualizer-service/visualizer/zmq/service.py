import asab
import logging
import imagezmq
from ext_lib.utils import get_imagezmq
import time
from asab import LOG_NOTICE

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
        self.ZeroMQVisualizerService = app.get_service("visualizer.ZeroMQVisualizerService")
        self.OpenCVVisualizerService = app.get_service("visualizer.OpenCVVisualizerService")
        self.RTSPVisualizerService = app.get_service("visualizer.RTSPVisualizerService")

        self.zmq_receiver = None
        self.zmq_publisher = None
        self._mode = asab.Config["stream:config"]["mode"]

    async def set_zmq_recv(self):
        uri = "tcp://%s:%s" % (asab.Config["zmq"]["sender_host"], asab.Config["zmq"]["sender_port"])
        L.log(LOG_NOTICE, "[IMPORTANT] Accepted ZMQ URL: {}".format(uri))
        self.zmq_receiver = imagezmq.ImageHub(open_port=uri, REQ_REP=False)

    async def set_zmq_output_publisher(self):
        if self._mode == "zeromq":
            uri = "tcp://%s:%s" % (asab.Config["stream:config"]["zeromq_host"], asab.Config["stream:config"]["zeromq_port"])
            L.log(LOG_NOTICE, "[IMPORTANT] Publish Image into this URL: {}".format(uri))
            self.zmq_publisher = imagezmq.ImageSender(connect_to=uri, REQ_REP=False)

    def get_zmq_receiver(self):
        return self.zmq_receiver

    async def _set_zmq_configurations(self):
        await self.set_zmq_recv()
        await self.set_zmq_output_publisher()

    async def start(self):
        await self._set_zmq_configurations()
        L.log(LOG_NOTICE, "I am running ...")

        if self._mode == "zeromq":
            await self.ZeroMQVisualizerService.run(self.get_zmq_receiver(), self.zmq_publisher)
        elif self._mode == "opencv":
            await self.OpenCVVisualizerService.run(self.get_zmq_receiver())
        else:
            await self.RTSPVisualizerService.run(self.get_zmq_receiver())
