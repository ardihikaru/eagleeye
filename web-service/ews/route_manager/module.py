import asab
from .service import RouteManagerService
from .handler import RouteWebHandler
from .rthandler import WebRealtimeHandler
from ext_lib.utils import get_current_time
import logging
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class RouteManagerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = RouteManagerService(app)
		self.WebHandler = RouteWebHandler(app)
		self.WebRTHandler = WebRealtimeHandler(app)

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Initialize RouteManagerModule." % get_current_time())

