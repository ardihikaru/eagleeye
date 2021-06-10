import asab
from asab import LOG_NOTICE
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import pubsub_to_json, get_current_time
from ext_lib.redis.translator import pub, redis_set, redis_get
import time
import simplejson as json
import requests
from enum import Enum

###

L = logging.getLogger(__name__)


###


class OffloadedDataBuilderService(asab.Service):
	class VideoSourceType(Enum):
		FOLDER = "FOLDER"
		STREAM = "STREAM"
		IMAGE_ZMQ = "IMAGEZMQ"
		TCP = "TCP"
		ZENOH = "ZENOH"

	""" A class to extract images"""
	def __init__(self, app, service_name="offloader.OffloadedDataBuilderService"):
		super().__init__(app, service_name)

		# services
		# self.ResizerService = app.get_service("scheduler.ResizerService")
		self.zmq_svc = app.get_service("eagleeye.ZMQService")
		self.img_consumer_svc = app.get_service("offloader.ImgConsumerService")
		# self.SchPolicyService = app.get_service("scheduler.SchedulingPolicyService")
		# self.TCPCameraServerService = app.get_service("scheduler.TCPCameraServerService")

		# start pub/sub
		self.redis = MyRedis(asab.Config)
		self.rc = self.redis.get_rc()

		# Get node information
		# self.node_api_uri = asab.Config["eagleeye:api"]["node"]

		# ZMQ Sender
		self.zmq_host = asab.Config["zmq"]["sender_host"]
		# self.zmq_sender = []

	async def subscribe_and_build_zenoh_consumer(self):
		L.log(LOG_NOTICE, "ReaderHandler try to consume the published data")

		# TODO: how to let the user to stop current subscription?
		# TODO: how to do restart?
		# set default config value
		config = {
			"valid": False
		}
		channel = asab.Config["pubsub:channel"]["scheduler"]
		consumer = self.rc.pubsub()
		consumer.subscribe([channel])
		for item in consumer.listen():
			if isinstance(item["data"], int):
				pass
			else:
				'''
				Expected object value:
				{
					"algorithm": "YOLOv3",
					"stream": true,
					"uri": "/app/data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4",
					"scalable": true
				}

				atau (Latest with ZENOH mode):
				{
				  'algorithm': 'YOLOv3',
				  'uri': 'tcp/localhost:7446',
				  'scalable': True,
				  'stream': 'ZENOH',
				  'extras': {
								'selector': '/ddr/svc/**'
							},
				  'timestamp': 1623300656.047577
				}
				'''

				# Set ZMQ configuration based on the available nodes
				await self.zmq_svc.set_configurations()

				# TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
				config = pubsub_to_json(item["data"])

				# TODO: validate whether the current config contains valid inputs or not
				config["valid"] = True
				# break

				# outside PubSub
				if config["valid"]:
					# Run ONCE due to the current capability to capture only one video stream
					t0_data = config["timestamp"]
					t1_data = (time.time() - t0_data) * 1000
					L.log(LOG_NOTICE, '\n #### [%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_data))
					# TODO: Saving latency for offloader:consumer

					# TODO: to re-implement other protocols: (1) ZeroMQ and (2) Plain TCP
					if config["stream"].upper() == self.VideoSourceType.ZENOH.value:
						await self.img_consumer_svc.start_zenoh_consumer(config)
					# elif config["stream"].upper() == self.VideoSourceType.TCP.value:
					# 	await self.ExtractorService.extract_image_tcp(config)
					# elif config["stream"].upper() == self.VideoSourceType.IMAGE_ZMQ.value:
					# 	await self.ExtractorService.extract_image_zmq(config)
					# elif config["stream"].upper() == self.VideoSourceType.STREAM.value:
					# 	await self.ExtractorService.extract_video_stream(config)
					# elif config["stream"].upper() == self.VideoSourceType.FOLDER.value:
					# 	await self.ExtractorService.extract_folder(config)
					else:
						L.error("## No images can be captured for the time being.")

				# L.log(LOG_NOTICE, "## System is no longer consuming data")
				L.log(LOG_NOTICE, "## MENUNGGU PubSub baru ## ")

		# start Redis subscription again
		# perform a recursive action
		await self.subscribe_and_build_zenoh_consumer()
