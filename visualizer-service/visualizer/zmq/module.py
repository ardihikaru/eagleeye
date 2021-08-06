import asab
from .service import ZMQService
from ext_lib.utils import get_current_time
import logging
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class ZMQModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = ZMQService(app, "visualizer.ZMQService")

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Initialize ZMQModule." % get_current_time())
