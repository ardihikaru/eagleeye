import asab
from .service import ZMQService
from ext_lib.utils import get_current_time


class ZMQModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = ZMQService(app, "detection.ZMQService")

	async def initialize(self, app):
		print("\n[%s] Initialize ZMQModule." % get_current_time())
