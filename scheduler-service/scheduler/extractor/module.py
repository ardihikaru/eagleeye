import asab
from .service import ExtractorService


class ExtractorModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = ExtractorService(app, "scheduler.ExtractorService")
