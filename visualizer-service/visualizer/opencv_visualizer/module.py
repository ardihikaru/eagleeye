import asab
from .service import OpenCVVisualizerService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class OpenCVVisualizerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = OpenCVVisualizerService(app, "visualizer.OpenCVVisualizerService")

	async def initialize(self, app):
		L.warning("\n[%s] Initialize OpenCVVisualizerModule." % get_current_time())
