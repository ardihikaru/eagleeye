import asab
from .service import ResizerService
from ext_lib.utils import get_current_time
import logging
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class ResizerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = ResizerService(app, "detection.ResizerService")

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Initialize ResizerModule." % get_current_time())
