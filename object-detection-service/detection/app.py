import asab.storage
import asab.web.session
from detection.zmq import ZMQModule
from detection.algorithm import AlgorithmModule
from ext_lib.utils import get_current_time
from mongoengine import connect


class ObjectDetectionService(asab.Application):

	# def __init__(self, opt):
	def __init__(self):
		super().__init__()

		# Connect Database
		connect('eagleeyeDB')

		# Loading the web service module
		self.add_module(asab.storage.Module)

		# Add modules
		self.add_module(ZMQModule)
		self.add_module(AlgorithmModule)

		# Initialize reader service
		self.AlgorithmService = self.get_service("detection.AlgorithmService")

	async def initialize(self):
		print("\n[%s] Object Detection Service is running!" % get_current_time())

		# Testing lah
		# storage = self.get_service("asab.StorageService")
		# coll = await storage.collection("Users")
		# cursor = coll.find({})
		# print("Result of list")
		# while await cursor.fetch_next:
		# 	obj = cursor.next_object()
		# 	print(obj)

		# Start subscription
		# await self.AlgorithmService.start_subscription()
		try:
			await self.AlgorithmService.start_subscription()
		except:
			print("\n[%s] This Object Detection Service has successfully stopped." % get_current_time())
