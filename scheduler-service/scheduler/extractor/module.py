import asab
from .service import ExtractorService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class ExtractorModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = ExtractorService(app, "scheduler.ExtractorService")

	async def initialize(self, app):
		# print("\n[%s] Initialize ExtractorModule." % get_current_time())
		L.warning("\n[%s] Initialize ExtractorModule." % get_current_time())
