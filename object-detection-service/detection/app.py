import asab.storage
import asab.web.session
from detection.latency_collector import LatencyCollectorModule
from detection.zmq import ZMQModule
from detection.resizer import ResizerModule
from detection.candidate_selection import CandidateSelectionModule
from detection.persistence_validation import PersistenceValidationModule
from detection.algorithm import DetectionAlgorithmModule
from ext_lib.utils import get_current_time
from mongoengine import connect
import logging

###

L = logging.getLogger(__name__)


###


class ObjectDetectionService(asab.Application):

	def __init__(self):
		super().__init__()

		# Set node alias
		self.node_alias = "NODE-%s" % asab.Config["node"]["name"]

		# Connect Database
		connect('eagleeyeDB')

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
