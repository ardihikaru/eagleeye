import asab
import asab.storage
from visualizer.fps_calculator import FPSCalculatorModule
from visualizer.gps_collector import GPSCollectorModule
from visualizer.zeromq_visualizer import ZeroMQVisualizerModule
from visualizer.opencv_visualizer import OpenCVVisualizerModule
from visualizer.rtsp_visualizer import RTSPVisualizerModule
from visualizer.image_publisher import ImagePublisherModule
from visualizer.image_plotter import ImagePlotterModule
from visualizer.zmq import ZMQModule
from ext_lib.utils import get_current_time
from missing_asab_components.application import Application
import os.path
from asab.log import LOG_NOTICE
import logging
from dotenv import load_dotenv, find_dotenv

###

L = logging.getLogger(__name__)


###


class VisualizerService(Application):

	def __init__(self):
		# IMPORTANT: Load `.env` file in this directory (if any)
		# Currently it is used for local deployment, Dockfile may not COPY this `.env` into the container yet
		if os.path.isfile(".env"):
			load_dotenv(find_dotenv())

		super().__init__()

		# Add customized modules
		self.add_module(FPSCalculatorModule)
		self.add_module(GPSCollectorModule)
		self.add_module(ImagePublisherModule)
		self.add_module(ImagePlotterModule)
		self.add_module(ZeroMQVisualizerModule)
		self.add_module(OpenCVVisualizerModule)
		self.add_module(RTSPVisualizerModule)
		self.add_module(ZMQModule)

		# Initialize ZMQ service
		self.ZMQService = self.get_service("visualizer.ZMQService")

	async def initialize(self):
		await self.ZMQService.start()
		L.warning("\n[%s]Visualize Service is running!" % get_current_time())
