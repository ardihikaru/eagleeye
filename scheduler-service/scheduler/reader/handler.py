import asab
import logging
import time
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import pubsub_to_json, get_current_time

###

L = logging.getLogger(__name__)


###

class ReaderHandler(MyRedis):

    def __init__(self, app):
        super().__init__(asab.Config)
        # print(" # @ ReaderHandler ...")
        self.ReaderService = app.get_service("scheduler.ReaderService")
        # self.ZMQService = app.get_service("scheduler.ZMQService")

        # Extractor service may not exist at this point
        # This variable will be set up in the init time
        # of ServiceAPIModule
        self.ExtractorService = None

    async def set_zmq_configurations(self):
        # await self.ZMQService.set_configurations()
        await self.ExtractorService.ZMQService.set_configurations()

    async def start(self):
        # print(">>>>>> START")
        # await self.ExtractorService.ZMQService.set_configurations()
        # print(">>>> SET ZMQ CONF FINISH")

        print("\n[%s] ReaderHandler try to consume the published data" % get_current_time())

        # Scheduler-service will ONLY handle a single stream, once it starts, ignore other input stream
        # TODO: To allow capturing multiple video streams (Future work)

        channel = asab.Config["pubsub:channel"]["scheduler"]
        consumer = self.rc.pubsub()
        consumer.subscribe([channel])
        for item in consumer.listen():
            if isinstance(item["data"], int):
                pass
            else:
                # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
                config = pubsub_to_json(item["data"])

                print(" >>> masuk lg nih ..")

                # Run ONCE due to the current capability to capture only one video stream
                # TODO: To allow capturing multiple video streams (Future work)
                t0_data = config["timestamp"]
                t1_data = (time.time() - t0_data) * 1000
                print('\n #### [%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_data))
                # TODO: Saving latency for scheduler:consumer

                print("Once data collected, try extracting data..")
                if config["stream"]:
                    await self.ExtractorService.extract_video_stream(config)
                else:
                    await self.ExtractorService.extract_folder(config)
                print("## No images can be captured for the time being.")

                # TODO: To restart; This should be moved away in extract_video_stream() and extract_folder()

        print("## System is no longer consuming data")
