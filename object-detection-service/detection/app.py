import asab.storage
import asab.web.session
from detection.yolov3 import YOLOv3Module
from ext_lib.utils import get_current_time


class ObjectDetectionService(asab.Application):

	# def __init__(self, opt):
	def __init__(self):
		super().__init__()

		# self.opt = opt
		# print(">>>> node ID: ", opt.node)

		# Loading the web service module
		self.add_module(asab.storage.Module)

		# Add reader module
		self.add_module(YOLOv3Module)

		# Initialize reader service
		self.YOLOv3Service = self.get_service("detection.YOLOv3Service")

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
		await self.YOLOv3Service.start_subscription()
