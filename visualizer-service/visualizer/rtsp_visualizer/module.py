import asab
from .service import RTSPVisualizerService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class RTSPVisualizerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = RTSPVisualizerService(app, "visualizer.RTSPVisualizerService")

	async def initialize(self, app):
		L.warning("\n[%s] Initialize RTSPVisualizerModule." % get_current_time())
