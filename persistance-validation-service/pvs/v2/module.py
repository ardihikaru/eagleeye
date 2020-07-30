import asab
from .service import PVSv2Service
from ext_lib.utils import get_current_time


class PVSv2Module(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = PVSv2Service(app, "pvs.PVSv2Service")

	async def initialize(self, app):
		print("\n[%s] Initialize PVSv2Module." % get_current_time())
