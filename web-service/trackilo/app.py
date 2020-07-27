import asab
import asab.web
import asab.web.rest
import asab.web.session
from trackilo.route_manager import RouteManagerModule
from mongoengine import connect


class TrackiloWebService(asab.Application):

	def __init__(self):
		super().__init__()

		# Connect Database
		connect('trackiloDB')

		# Web module/service
		self.add_module(asab.web.Module)
		self.add_module(RouteManagerModule)

	async def initialize(self):
		print("Trackilo Web Service is running!")
