import asab.storage
import asab.web.session
from css.v1 import CSSv1Module
from css.v2 import CSSv2Module
from ext_lib.utils import get_current_time


class CandidateSelectionService(asab.Application):

	def __init__(self):
		super().__init__()

		# Loading the web service module
		self.add_module(asab.storage.Module)

		# Add reader module
		self.add_module(CSSv1Module)
		self.add_module(CSSv2Module)
		# TODO: To have another Module which enable to perform switching based on the input configuration

		# Initialize reader service
		# TODO: To finish the algorithm implementation of CSSv1
		# TODO: To finish the algorithm implementation of CSSv2
		# self.CSSService = self.get_service("css.CSSv1Service")
		self.CSSService = self.get_service("css.CSSv2Service")

	async def initialize(self):
		print("\n[%s] Candidate Selection Service is running!" % get_current_time())

		# Start subscription
		await self.CSSService.start_subscription()
