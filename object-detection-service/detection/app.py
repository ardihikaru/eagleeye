import asab.storage
import asab.web.session
from detection.zmq import ZMQModule
from detection.algorithm import DetectionAlgorithmModule
from ext_lib.utils import get_current_time
from mongoengine import connect


class ObjectDetectionService(asab.Application):

	def __init__(self):
		super().__init__()

		# Connect Database
		connect('eagleeyeDB')

		# Loading the web service module
		self.add_module(asab.storage.Module)

		# Add modules
		self.add_module(ZMQModule)
		self.add_module(DetectionAlgorithmModule)

		# Initialize reader service
		self.DetectionAlgorithmService = self.get_service("detection.DetectionAlgorithmService")

	async def initialize(self):
		print("\n[%s] Object Detection Service is running!" % get_current_time())

		# Start subscription
		try:
			await self.DetectionAlgorithmService.start_subscription()
		except:
			print("\n[%s] This Object Detection Service has successfully stopped." % get_current_time())
