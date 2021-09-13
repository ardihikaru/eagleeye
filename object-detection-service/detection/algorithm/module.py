import asab
from .service import DetectionAlgorithmService
from ext_lib.utils import get_current_time
import logging
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class DetectionAlgorithmModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = DetectionAlgorithmService(app, "detection.DetectionAlgorithmService")

	async def initialize(self, app):
		self.Service.ZMQService = app.get_service('detection.ZMQService')
		L.log(LOG_NOTICE, "[{}] Initialize DetectionAlgorithmModule.".format(get_current_time()))
