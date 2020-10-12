import asab
from .service import GPSCollectorService


class GPSCollectorModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = GPSCollectorService(app)
