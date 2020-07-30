import asab
from .service import CSSv1Service
from ext_lib.utils import get_current_time


class CSSv1Module(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = CSSv1Service(app, "css.CSSv1Service")

	async def initialize(self, app):
		print("\n[%s] Initialize CSSv1Module." % get_current_time())
