import asab
from .service import AlgorithmService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class AlgorithmModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = AlgorithmService(app, "pv.AlgorithmService")

	async def initialize(self, app):
		L.warning("\n[%s] Initialize Algorithm Module." % get_current_time())
