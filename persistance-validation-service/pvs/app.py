import asab.storage
import asab.web.session
from pvs.v1 import PVSv1Module  # TODO: To implement our current work here
# from pvs.v2 import PVSv2Module  # TODO: Future work
from ext_lib.utils import get_current_time


class CandidateSelectionService(asab.Application):

	def __init__(self):
		super().__init__()

		# Loading the web service module
		self.add_module(asab.storage.Module)

		# Add reader module
		self.add_module(PVSv1Module)
		# self.add_module(PVSv2Module)
		# TODO: To have another Module which enable to perform switching based on the input configuration

		# Initialize reader service
		# TODO: To finish the algorithm implementation of PVSv1
		self.PVSService = self.get_service("pvs.PVSv1Service")

	async def initialize(self):
		print("\n[%s] Persistance Validation is running!" % get_current_time())

		# Start subscription
		await self.PVSService.start_subscription()
