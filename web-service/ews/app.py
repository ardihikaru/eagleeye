import asab
import asab.web
import asab.web.rest
import asab.web.session
from ews.route_manager import RouteManagerModule
from ext_lib.redis.my_redis import MyRedis
from mongoengine import connect
from mongoengine.connection import _get_db


class EagleEYEWebService(asab.Application):

	def __init__(self):
		super().__init__()

		# Connect Database
		connect('eagleeyeDB')

		# Delete all keys in redis as the application runs
		redis = MyRedis(asab.Config)
		redis.delete_all_keys()

		# Drop Collection: `Configs`, `Nodes` and `Latency`
		db = _get_db()
		db["Nodes"].drop()
		# db["Latency"].drop()
		db["Configs"].drop()

		# Web module/service
		self.add_module(asab.web.Module)
		self.add_module(RouteManagerModule)

	async def initialize(self):
		print("EagleEYE Web Service is running!")
