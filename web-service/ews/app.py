import asab
import asab.web
import asab.web.rest
import asab.web.session
from ews.route_manager import RouteManagerModule
from ews.aio_rtc import AIORTCModule
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_set
from mongoengine import connect
from mongoengine.connection import _get_db
import logging

###

L = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

###


class EagleEYEWebService(asab.Application):

	def __init__(self):
		super().__init__()

		# Connect Database
		connect('eagleeyeDB', host=asab.Config["asab:storage"]["mongodb_host"])

		# Delete all keys in redis as the application runs
		redis = MyRedis(asab.Config)
		redis.delete_all_keys()

		# Add initial total active worker nodes
		redis_set(redis.get_rc(), asab.Config["redis"]["total_worker_key"], 0)

		# Drop Collection: `Configs`, `Nodes` and `Latency`
		db = _get_db()
		db["Nodes"].drop()
		db["Latency"].drop()
		db["Configs"].drop()

		# Web module/service
		self.add_module(asab.web.Module)
		self.add_module(AIORTCModule)
		self.add_module(RouteManagerModule)

	async def initialize(self):
		L.warning("EagleEYE Web Service is running!")
