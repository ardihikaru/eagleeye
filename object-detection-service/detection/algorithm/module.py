import asab
from .service import DetectionAlgorithmService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class DetectionAlgorithmModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = DetectionAlgorithmService(app, "detection.DetectionAlgorithmService")

	async def initialize(self, app):
		self.Service.ZMQService = app.get_service('detection.ZMQService')
		# print("\n[%s] Initialize DetectionAlgorithmModule." % get_current_time())
		L.warning("\n[%s] Initialize DetectionAlgorithmModule." % get_current_time())
