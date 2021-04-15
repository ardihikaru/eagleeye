import asab
from .service import PVApiService
from .handler import PVApiWebHandler
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class PVApiModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = PVApiService(app)
		self.PVApiWebHandler = PVApiWebHandler(app)

	async def initialize(self, app):
		L.warning("\n[%s] Initialize PV Api Module." % get_current_time())
