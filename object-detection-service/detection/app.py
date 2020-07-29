import asab
import asab.web.session
from detection.yolov3 import YOLOv3Module
from mongoengine import connect
from ext_lib.utils import get_current_time


class ObjectDetectionService(asab.Application):

	def __init__(self):
		super().__init__()

		# Connect Database
		connect('eagleeyeDB')
		
		# Add reader module
		self.add_module(YOLOv3Module)

		# Initialize reader service
		self.YOLOv3Service = self.get_service("detection.YOLOv3Service")

	async def initialize(self):
		print("\n[%s] Object Detection Service is running!" % get_current_time())
		# Start subscription
		await self.YOLOv3Service.start_subscription()
