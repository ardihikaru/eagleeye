import asab
from .service import CSSv2Service
from ext_lib.utils import get_current_time


class CSSv2Module(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = CSSv2Service(app, "css.CSSv2Service")

	async def initialize(self, app):
		print("\n[%s] Initialize CSSv2Module." % get_current_time())
