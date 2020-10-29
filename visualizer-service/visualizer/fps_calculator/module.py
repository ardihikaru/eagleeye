import asab
from .service import FPSCalculatorService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class FPSCalculatorModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = FPSCalculatorService(app, "visualizer.FPSCalculatorService")

	async def initialize(self, app):
		L.warning("\n[%s] Initialize FPSCalculatorModule." % get_current_time())
