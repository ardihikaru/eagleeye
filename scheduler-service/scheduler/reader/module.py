import asab
from .service import ReaderService
from .handler import ReaderHandler


class ReaderModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		print(" -- @ ReaderModule...")
		self.Service = ReaderService(app, "ReaderService")
		self.SubscriptionHandler = ReaderHandler(app)

	async def initialize(self, app):
		print(" --- initialize @ ReaderModule ..")
		self.SubscriptionHandler.ExtractorService = app.get_service('scheduler.ExtractorService')
		self.SubscriptionHandler.start()
		# self.Handler.IdentityService = app.get_service('ecr.IdentityService')
