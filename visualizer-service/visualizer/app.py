import asab
import asab.storage
from visualizer.gps_collector import GPSCollectorModule
from visualizer.opencv_visualizer import OpenCVVisualizerModule
from visualizer.image_publisher import ImagePublisherModule
from visualizer.image_plotter import ImagePlotterModule
from visualizer.zmq import ZMQModule
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class VisualizerService(asab.Application):

	def __init__(self):
		super().__init__()

		# Add customized modules
		self.add_module(GPSCollectorModule)
		self.add_module(ImagePublisherModule)
		self.add_module(ImagePlotterModule)
		self.add_module(OpenCVVisualizerModule)
		self.add_module(ZMQModule)

		# Initialize ZMQ service
		self.ZMQService = self.get_service("visualizer.ZMQService")

	async def initialize(self):
		await self.ZMQService.start()
		L.warning("\n[%s]Visualize Service is running!" % get_current_time())
