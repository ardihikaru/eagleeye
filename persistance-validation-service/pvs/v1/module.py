import asab
from .service import PVSv1Service
from ext_lib.utils import get_current_time


class PVSv1Module(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = PVSv1Service(app, "pvs.PVSv1Service")

	async def initialize(self, app):
		print("\n[%s] Initialize PVSv1Module." % get_current_time())
