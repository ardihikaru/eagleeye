import asab
from .service import RouteManagerService
from .handler import RouteWebHandler
from .rthandler import WebRealtimeHandler


class RouteManagerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = RouteManagerService(app)
		self.WebHandler = RouteWebHandler(app)
		self.WebRTHandler = WebRealtimeHandler(app)
