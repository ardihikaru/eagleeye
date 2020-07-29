import asyncio
import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time, pubsub_to_json
import time

###

L = logging.getLogger(__name__)


###


class ExtractorService(asab.Service):
    """
        A class to extract either: Video stream or tuple of images
    """

    def __init__(self, app, service_name="scheduler.ExtractorService"):
        super().__init__(app, service_name)

        # start pub/sub
        self.redis = MyRedis(asab.Config)
        # self._run()

    def extract(self):
        print("#### I am extractor function from ExtractorService!")
    # def _run(self):
    #     channel = asab.Config["pubsub:channel"]["scheduler"]
    #     consumer = self.redis.get_rc().pubsub()
    #     consumer.subscribe([channel])
    #     for item in consumer.listen():
    #         if isinstance(item["data"], int):
    #             pass
    #         else:
    #             request_data = pubsub_to_json(item["data"])
    #             t0_data = request_data["timestamp"]
    #             t1_data = (time.time() - t0_data) * 1000
    #             print('\n #### [%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_data))
    #             # TODO: Saving latency for scheduler:consumer
