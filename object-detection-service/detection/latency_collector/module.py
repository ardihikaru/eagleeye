import asab
from .service import LatencyCollectorService
from ext_lib.utils import get_current_time


class LatencyCollectorModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = LatencyCollectorService(app, "detection.LatencyCollectorService")

	async def initialize(self, app):
		print("\n[%s] Initialize LatencyCollectorModule." % get_current_time())
