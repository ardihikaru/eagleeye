import asab
from asab import LOG_NOTICE
import asyncio
import time
import numpy as np
from datetime import datetime
from zenoh_lib.zenoh_net_subscriber import ZenohNetSubscriber
import logging

from concurrent.futures import ThreadPoolExecutor
import cv2
import requests

###

L = logging.getLogger(__name__)


###

class ZenohImageSubscriberService(asab.Service):

	class ErrorCode(object):
		ERR_ZENOH_MODE = "system_err_001"
		ERR_ZENOH_SUBSCRIPTION = "system_err_002"
		ERR_REDIS_MODE = "system_err_003"
		ERR_SUBSCRIPTION_SELECTOR = "system_err_004"
		ERR_STITCHING_MODE = "system_err_005"

	class PubSubMode(object):
		ZENOH = "zenoh"
		REDIS = "redis"

	class ZenohConsumerType(object):
		NON_COMPRESSION_TAGGED_IMAGE = 3
		COMPRESSION_TAGGED_IMAGE = 4

	def __init__(self, app, service_name="eagleeye.ZenohImageSubscriberService"):
		super().__init__(app, service_name)

		# load services
		self.system_manager = app.get_service('eagleeye.SystemManagerService')

		# config zenoh pubsub config (default)
		self.zenoh_dy_conf = asab.Config["zenoh"]["dynamic"]
		self.zenoh_comm_protocol = None
		self.zenoh_comm_ip = None
		self.zenoh_comm_port = None
		self.selector = None
		self.listener = None
		self.sub_svc = None
		self.subscriber = None

		self.log_initialized = False
		self.consumer_is_running = False

		# self.pubsub_mode = asab.Config["pubsub:config"]["mode"]
		# self.drone_api_uri = asab.Config["drone"]["root_api_url"]

		self.executor = ThreadPoolExecutor(1)

	async def initialize(self, app):
		# setup default value
		if not self.zenoh_dy_conf:
			self.zenoh_comm_protocol = asab.Config["zenoh"]["comm_protocol"]
			self.zenoh_comm_ip = asab.Config["zenoh"]["comm_ip"]
			self.zenoh_comm_port = asab.Config["zenoh"]["comm_port"]
			self.selector = asab.Config["zenoh"]["selector"]
			self.listener = "{}/{}:{}".format(
				self.zenoh_comm_protocol,
				self.zenoh_comm_ip,
				self.zenoh_comm_port,
			)

	async def override_zenoh_config(self, config):
		self.selector = config["extras"]["selector"]
		self.listener = config["uri"]

	# WILL BE OVERRIDED BY PARENT CLASS
	def img_listener(self, consumed_data):
		pass
		# sample codes
		# img_info, latency_data = extract_compressed_tagged_img(consumed_data)

		# DO SOMETHING HERE

	def _start_zenoh(self):
		# after being called ONCE, set as True
		# it avoid multiple initialization of Zenoh Logger
		self.log_initialized = True

		self.sub_svc = ZenohNetSubscriber(
			_selector=self.selector, _session_type="SUBSCRIBER", _listener=self.listener
		)
		time.sleep(2)
		self.sub_svc.init_connection(self.log_initialized)
		# self.sub_svc.init_connection()

		time.sleep(2)
		self.sub_svc.register(self.img_listener)
		self.subscriber = self.sub_svc.get_subscriber()
		time.sleep(2)

		# update streaming status
		# only ONE CONSUMER IS ALLOWED TO RUN
		self.consumer_is_running = True

	# once module stopped, stop the subscription
	async def finalize(self, app):
		await self._stop_subscription()

	async def shutdown_executor(self):
		self.executor.shutdown()
		self.executor = None

		return True

	async def close_zenoh_session(self):
		self.sub_svc.close_connection(self.subscriber)

		return True

	async def start_zenoh_subscription(self):
		L.log(LOG_NOTICE, "[ZENOH_CONSUMER] Start Listening . . .")

		# TODO: fix error: IO error () at /home/ardi/.cargo/git/checkouts/zenoh-..../orchestrator.rs:304. - Caused by
		#  Invalid link (Can not create a new TCP listener on 127.0.0.1:7446: Address already in use (os error 98)) at
		#  /home/ardi/.cargo/git/checkouts/zenoh-cc237f2570fab813/786b602/zenoh/src/net/protocol/link/tcp.rs:333. if
		#  zenoh instance is currently active, destroy it first!
		if self.consumer_is_running:
			await self.close_zenoh_session()  # close zenoh session
			await asyncio.sleep(2)  # wait for 2 secs
			await self.shutdown_executor()  # kill running executor
			await asyncio.sleep(2)  # wait for 2 secs

		try:
			self.executor = ThreadPoolExecutor(1)
			self.executor.submit(self._start_zenoh)

		except Exception as e:
			print(" @@@ ERROORRR #$### ")
			_err_msg = ">>>>> ZENOH Subscription Failed; Reason: `{}`".format(e)
			L.error(_err_msg)
			await self.system_manager.publish_error(
				system_code=self.ErrorCode.ERR_ZENOH_SUBSCRIPTION,
				system_message=_err_msg
			)

	async def _stop_subscription(self):
		try:
			self.sub_svc.close_connection(self.subscriber)
		except AttributeError as e:
			pass

	async def subscription(self):
		await self._start_zenoh_subscription()
