import asab
import asab.storage
import asab.web.session
from detection.gps_collector import GPSCollectorModule
from latency.module import LatencyCollectorModule
from detection.zmq import ZMQModule
from detection.resizer import ResizerModule
from detection.algorithm import DetectionAlgorithmModule
from ext_lib.utils import get_current_time
import logging
from missing_asab_components.application import Application
import os.path
from asab.log import LOG_NOTICE
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_get
from dotenv import load_dotenv, find_dotenv

###

L = logging.getLogger(__name__)


###


class ObjectDetectionService(Application):

	def __init__(self):
		# IMPORTANT: Load `.env` file in this directory (if any)
		# Currently it is used for local deployment, Dockfile may not COPY this `.env` into the container yet
		if os.path.isfile(".env"):
			load_dotenv(find_dotenv())

		super().__init__()

		# # Testing:
		# import os
		# PYTHONPATH = os.getenv("PYTHONPATH")
		# print(" this is PYTHONPATH:", PYTHONPATH)

		# Set node alias
		redis = MyRedis(asab.Config)
		node_name = redis_get(redis.get_rc(), asab.Config["node"]["redis_name_key"])
		self.node_alias = "NODE-%s" % str(node_name)

		# Loading the web service module
		self.add_module(asab.storage.Module)

		# Add modules
		self.add_module(GPSCollectorModule)
		self.add_module(LatencyCollectorModule)
		self.add_module(ZMQModule)
		self.add_module(ResizerModule)
		self.add_module(DetectionAlgorithmModule)

		# Initialize reader service
		self.DetectionAlgorithmService = self.get_service("detection.DetectionAlgorithmService")

	async def initialize(self):
		L.log(LOG_NOTICE, "[%s][%s] Object Detection Service is running!" % (get_current_time(), self.node_alias))

		# Start subscription
		try:
			await self.DetectionAlgorithmService.start_subscription()
		except:
			L.log(LOG_NOTICE, "[{}][{}] This Object Detection Service has successfully stopped.".format(
				get_current_time(), self.node_alias))
