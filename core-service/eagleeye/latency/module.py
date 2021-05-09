import asab
from ext_lib.utils import get_current_time
from latency.service import LatencyCollectorService
import logging

###

L = logging.getLogger(__name__)


###


class LatencyCollectorModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = LatencyCollectorService(app, "eagleeye.LatencyCollectorService")

	async def initialize(self, app):
		L.warning("\n[%s] Initialize Latency Collector Module." % get_current_time())
