import asab.web.session
from system_manager import SystemManagerModule
from latency.module import LatencyCollectorModule
from my_zmq.module import ZMQModule
from img_resizer.module import ResizerModule

from offloader.scheduling_policy import SchedulingPolicyModule
from offloader.offloaded_data_builder import OffloadedDataBuilderModule
from offloader.img_data_consumer import ImgConsumerModule

from ext_lib.utils import get_current_time
import logging
from missing_asab_components.application import Application
import os.path
from asab.log import LOG_NOTICE
from dotenv import load_dotenv, find_dotenv

###

L = logging.getLogger(__name__)


###


class OffloaderService(Application):

	def __init__(self):
		# IMPORTANT: Load `.env` file in this directory (if any)
		# Currently it is used for local deployment, Dockfile may not COPY this `.env` into the container yet
		if os.path.isfile(".env"):
			load_dotenv(find_dotenv())

		super().__init__()

		# Add reader module
		self.add_module(SystemManagerModule)
		self.add_module(LatencyCollectorModule)
		self.add_module(ResizerModule)
		self.add_module(ZMQModule)

		self.add_module(SchedulingPolicyModule)
		self.add_module(ImgConsumerModule)  # Zenoh Consumer
		self.add_module(OffloadedDataBuilderModule)  # Redis Subscriber

		# self.add_module(ImageSubscriberModule)
		# self.add_module(ReaderModule)

		# Initialize reader service
		# self.ReaderService = self.get_service("scheduler.ReaderService")
		self.offloader_data_bdr_svc = self.get_service("offloader.OffloadedDataBuilderService")

	async def initialize(self):
		# Start Redis subscription
		await self.offloader_data_bdr_svc.subscribe_and_build_zenoh_consumer()
