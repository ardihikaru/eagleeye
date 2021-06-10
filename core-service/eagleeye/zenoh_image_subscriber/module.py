import asab
import asyncio
from .service import ZenohImageSubscriberService
import logging
from asab.log import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class ZenohImageSubscriberModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = ZenohImageSubscriberService(app)

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[SYSTEM PREPARATION] Zenoh Image Subscriber Module is loaded.")
