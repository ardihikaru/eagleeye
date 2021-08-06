import asab
from .service import GPSCollectorService
from ext_lib.utils import get_current_time
import logging
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class GPSCollectorModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = GPSCollectorService(app)

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Initialize GPSCollectorModule." % get_current_time())
