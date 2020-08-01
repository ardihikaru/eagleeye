import asab
from .service import AlgorithmService
from ext_lib.utils import get_current_time


class AlgorithmModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = AlgorithmService(app, "detection.AlgorithmService")

	async def initialize(self, app):
		self.Service.ZMQService = app.get_service('detection.ZMQService')
		print("\n[%s] Initialize AlgorithmModule." % get_current_time())
