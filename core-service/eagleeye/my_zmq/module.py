import asab
from asab import LOG_NOTICE
from .service import ZMQService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class ZMQModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = ZMQService(app, "eagleeye.ZMQService")

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Initialize ZMQModule." % get_current_time())
