import asab
from .service import FrameIDConsumerService
from ext_lib.utils import get_current_time
import logging
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class FrameIDConsumerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = FrameIDConsumerService(app)

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Initialize Frame ID Consumer Module." % get_current_time())

		# start subscription
		await self.Service.start_subscription()
