import asab
from .service import CandidateSelectionService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class CandidateSelectionModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = CandidateSelectionService(app, "detection.CandidateSelectionService")

	async def initialize(self, app):
		# print("\n[%s] Initialize CandidateSelectionModule." % get_current_time())
		L.warning("\n[%s] Initialize CandidateSelectionModule." % get_current_time())
