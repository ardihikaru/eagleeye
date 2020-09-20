import asab
import asab.storage
import asab.web.session
from detection.latency_collector import LatencyCollectorModule
from detection.zmq import ZMQModule
from detection.resizer import ResizerModule
from detection.candidate_selection import CandidateSelectionModule
from detection.persistence_validation import PersistenceValidationModule
from detection.algorithm import DetectionAlgorithmModule
from ext_lib.utils import get_current_time
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_get

###

L = logging.getLogger(__name__)


###


class ObjectDetectionService(asab.Application):

	def __init__(self):
		super().__init__()

		# Set node alias
		redis = MyRedis(asab.Config)
		node_name = redis_get(redis.get_rc(), asab.Config["node"]["redis_name_key"])
		self.node_alias = "NODE-%s" % str(node_name)

		# Loading the web service module
		self.add_module(asab.storage.Module)

		# Add modules
		self.add_module(LatencyCollectorModule)
		self.add_module(ZMQModule)
		self.add_module(ResizerModule)
		self.add_module(CandidateSelectionModule)
		self.add_module(PersistenceValidationModule)
		self.add_module(DetectionAlgorithmModule)

		# Initialize reader service
		self.DetectionAlgorithmService = self.get_service("detection.DetectionAlgorithmService")

	async def initialize(self):
		# print("\n[%s][%s] Object Detection Service is running!" % (get_current_time(), self.node_alias))
		L.warning("\n[%s][%s] Object Detection Service is running!" % (get_current_time(), self.node_alias))

		# Start subscription
		try:
			await self.DetectionAlgorithmService.start_subscription()
		except:
			# print("\n[%s][%s] This Object Detection Service has successfully stopped." % (get_current_time(), self.node_alias))
			L.warning("\n[%s][%s] This Object Detection Service has successfully stopped." % (get_current_time(), self.node_alias))
