import asab
from .service import PCSApiService
from .handler import PCSApiWebHandler
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class PCSApiModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = PCSApiService(app)
		self.PCSApiWebHandler = PCSApiWebHandler(app)

	async def initialize(self, app):
		L.warning("\n[%s] Initialize PCS Api Module." % get_current_time())
