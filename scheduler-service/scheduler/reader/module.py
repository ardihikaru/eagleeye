import asab
from .service import ReaderService
from ext_lib.utils import get_current_time


class ReaderModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = ReaderService(app, "scheduler.ReaderService")

	async def initialize(self, app):
		print("\n[%s] Initialize ReaderModule." % get_current_time())
