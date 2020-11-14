import asab
from .service import ZeroMQVisualizerService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class ZeroMQVisualizerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = ZeroMQVisualizerService(app, "visualizer.ZeroMQVisualizerService")

	async def initialize(self, app):
		L.warning("\n[%s] Initialize ZeroMQVisualizerModule." % get_current_time())
