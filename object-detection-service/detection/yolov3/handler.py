import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time

###

L = logging.getLogger(__name__)


###

class YOLOv3Handler(MyRedis):

    def __init__(self, app):
        super().__init__(asab.Config)
        self.ReaderService = app.get_service("detection.YOLOv3Service")

    async def start(self):
        print("\n[%s] YOLOv3Handler try to consume the published data from [Scheduler Service]" % get_current_time())

        # # Scheduler-service will ONLY handle a single stream, once it starts, ignore other input stream
        # # TODO: To allow capturing multiple video streams (Future work)
        # is_streaming = False
        # recognized_uri = None
        #
        # channel = asab.Config["pubsub:channel"]["scheduler"]
        # consumer = self.rc.pubsub()
        # consumer.subscribe([channel])
        # for item in consumer.listen():
        #     if isinstance(item["data"], int):
        #         pass
        #     else:
        #         # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
        #         config = pubsub_to_json(item["data"])
        #
        #         # Input source handler: To ONLY allow one video stream once started
        #         if recognized_uri is None:
        #             recognized_uri = config["uri"]
        #
        #         # Run ONCE due to the current capability to capture only one video stream
        #         # TODO: To allow capturing multiple video streams (Future work)
        #         if not is_streaming:
        #             is_streaming = True
        #             t0_data = config["timestamp"]
        #             t1_data = (time.time() - t0_data) * 1000
        #             print('\n #### [%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_data))
        #             # TODO: Saving latency for scheduler:consumer
        #
        #             print("Once data collected, try extracting data..")
        #             if config["stream"]:
        #                 await self.ExtractorService.extract_video_stream(config)
        #             else:
        #                 await self.ExtractorService.extract_folder(config)
        #
        #             # Stop watching once
        #             if "stop" in config:
        #                 print("### System is interrupted and asked to stop comsuming data.")
        #                 break
        #
        # print("## System is no longer consuming data")
