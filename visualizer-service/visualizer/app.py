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
import logging
from dotenv import load_dotenv, find_dotenv

###

L = logging.getLogger(__name__)


###


class VisualizerService(asab.Application):

	def __init__(self):
		super().__init__()

		# IMPORTANT: Load `.env` file
		load_dotenv(find_dotenv(filename=asab.Config["commons"]["envfile"]))
		# TODO: Update Dockerfile to COPY `.env` file to container

		# # Testing:
		# import os
		# PYTHONPATH = os.getenv("PYTHONPATH")
		# print(" this is PYTHONPATH:", PYTHONPATH)

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
