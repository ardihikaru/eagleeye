import asab
from asab import LOG_NOTICE
import logging
import time
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import pubsub_to_json, get_current_time
from enum import Enum

###

L = logging.getLogger(__name__)


###

class VideoSourceType(Enum):
	FOLDER = "FOLDER"
	STREAM = "STREAM"
	IMAGE_ZMQ = "IMAGEZMQ"
	TCP = "TCP"
	ZENOH = "ZENOH"


class ReaderHandler(MyRedis):

	def __init__(self, app):
		super().__init__(asab.Config)
		self.ReaderService = app.get_service("scheduler.ReaderService")
		# self.ZMQService = app.get_service("scheduler.ZMQService")

		# Extractor service may not exist at this point
		# This variable will be set up in the init time
		# of ServiceAPIModule
		self.ExtractorService = None

	async def set_zmq_configurations(self):
		await self.ExtractorService.ZMQService.set_configurations()

	async def start(self):
		L.log(LOG_NOTICE, "[%s] ReaderHandler try to consume the published data" % get_current_time())

		# Scheduler-service will ONLY handle a single stream, once it starts, ignore other input stream
		# TODO: To allow capturing multiple video streams (Future work)

		# is_configured = False

		channel = asab.Config["pubsub:channel"]["scheduler"]
		consumer = self.rc.pubsub()
		consumer.subscribe([channel])
		for item in consumer.listen():
			if isinstance(item["data"], int):
				pass
			else:
				# TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
				config = pubsub_to_json(item["data"])
				'''
					Expected object value:
					{
						"algorithm": "YOLOv3",
						"stream": true,
						"uri": "/app/data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4",
						"scalable": true
					}
				'''

				# Run ONCE due to the current capability to capture only one video stream
				# TODO: To allow capturing multiple video streams (Future work)
				t0_data = config["timestamp"]
				t1_data = (time.time() - t0_data) * 1000
				L.log(LOG_NOTICE, '#### [%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_data))
				# TODO: Saving latency for scheduler:consumer

				# print("Once data collected, try extracting data..")
				if config["stream"].upper() == VideoSourceType.TCP.value:
					await self.ExtractorService.extract_image_tcp(config)
				elif config["stream"].upper() == VideoSourceType.IMAGE_ZMQ.value:
					await self.ExtractorService.extract_image_zmq(config)
				elif config["stream"].upper() == VideoSourceType.STREAM.value:
					await self.ExtractorService.extract_video_stream(config)
				elif config["stream"].upper() == VideoSourceType.FOLDER.value:
					await self.ExtractorService.extract_folder(config)
				elif config["stream"].upper() == VideoSourceType.ZENOH.value:
					await self.ExtractorService.extract_image_zenoh(config)
				else:
					L.error("## No images can be captured for the time being.")

				# TODO: To restart; This should be moved away in extract_video_stream() and extract_folder()

		L.log(LOG_NOTICE, "## System is no longer consuming data")
