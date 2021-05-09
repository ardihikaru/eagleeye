import asab
from .service import SorterApiService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class SorterApiModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = SorterApiService(app)

	async def initialize(self, app):
		L.warning("\n[%s] Initialize Sorter Api Module." % get_current_time())

		# start subscription
		await self.Service.start_subscription()
