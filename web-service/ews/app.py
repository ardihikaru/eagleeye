import asab
import asab.web
import asab.web.rest
import asab.web.session
from ews.route_manager import RouteManagerModule
from mongoengine import connect


class EagleEYEWebService(asab.Application):

	def __init__(self):
		super().__init__()

		# Connect Database
		connect('eagleeyeDB')

		# Web module/service
		self.add_module(asab.web.Module)
		self.add_module(RouteManagerModule)

	async def initialize(self):
		print("EagleEYE Web Service is running!")
