import asab
import asab.web
import asab.web.rest
import asab.web.session
from ews.route_manager import RouteManagerModule
from ews.gps_collector import GPSCollectorModule
# from ews.aio_rtc import AIORTCModule
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_set
from mongoengine import connect
from mongoengine.connection import _get_db
import logging
from missing_asab_components.application import Application
import os.path
from asab.log import LOG_NOTICE
from ews.controllers.node.node import Node as NodeController
from dotenv import load_dotenv, find_dotenv

###

L = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

###


class EagleEYEWebService(Application):

	def __init__(self):
		# IMPORTANT: Load `.env` file in this directory (if any)
		# Currently it is used for local deployment, Dockfile may not COPY this `.env` into the container yet
		if os.path.isfile(".env"):
			load_dotenv(find_dotenv())

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
		# self.add_module(AIORTCModule)
		self.add_module(RouteManagerModule)
		self.add_module(GPSCollectorModule)

	async def initialize(self):
		# Register one worker node as default available worker node
		json_data = {
			"candidate_selection": True,
			"persistence_validation": True
		}
		NodeController().register(json_data)

		L.log(LOG_NOTICE, "EagleEYE Web Service is running!")
