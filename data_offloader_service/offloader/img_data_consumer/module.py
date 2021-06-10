import asab
from .service import ImgConsumerService
from ext_lib.utils import get_current_time
import logging
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class ImgConsumerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = ImgConsumerService(app, "offloader.ImgConsumerService")

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Initialize Img Consumer Module." % get_current_time())
