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
		self.Service = CandidateSelectionService(app, "pcs.CandidateSelectionService")

	async def initialize(self, app):
		L.warning("\n[%s] Initialize Candidate Selection Module." % get_current_time())
