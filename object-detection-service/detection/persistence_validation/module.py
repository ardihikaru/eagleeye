import asab
from .service import PersistenceValidationService
from ext_lib.utils import get_current_time


class PersistenceValidationModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = PersistenceValidationService(app, "detection.PersistenceValidationService")

	async def initialize(self, app):
		print("\n[%s] Initialize PersistenceValidationModule." % get_current_time())
