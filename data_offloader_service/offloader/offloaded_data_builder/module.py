import asab
from .service import OffloadedDataBuilderService
from ext_lib.utils import get_current_time
import logging
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class OffloadedDataBuilderModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = OffloadedDataBuilderService(app, "offloader.OffloadedDataBuilderService")

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Offloaded Data Builder Module." % get_current_time())
