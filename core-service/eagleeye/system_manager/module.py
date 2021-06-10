import asab
from .service import SystemManagerService
import logging
from asab.log import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class SystemManagerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = SystemManagerService(app)

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[System Manager Module] is loaded.")
