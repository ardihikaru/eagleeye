import asab
from .service import AIORTCService


class AIORTCModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = AIORTCService(app)
