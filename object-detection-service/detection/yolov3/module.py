import asab
from .service import YOLOv3Service
from ext_lib.utils import get_current_time


class YOLOv3Module(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = YOLOv3Service(app, "detection.YOLOv3Service")

	async def initialize(self, app):
		print("\n[%s] Initialize YOLOv3Module." % get_current_time())
