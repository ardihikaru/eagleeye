import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time
from detection.controllers.node.node import Node
import os

###

L = logging.getLogger(__name__)


###

class YOLOv3Handler(MyRedis):

    def __init__(self, app):
        super().__init__(asab.Config)
        self.YOLOv3Service = app.get_service("detection.YOLOv3Service")
        # self.storage = app.get_service("asab.StorageService")

        # Default None
        self.node_id = asab.Config["node"]["id"]
        self.pid = os.getpid()

    async def set_configuration(self):
        # Initialize YOLOv3 configuration
        print("\n[%s] Initialize YOLOv3 configuration" % get_current_time())

        # coll = await self.storage.collection("Users")
        # cursor = coll.find({})
        # print("Result of list *** DISINI ***")
        # while await cursor.fetch_next:
        #     obj = cursor.next_object()
        #     print(obj)

    async def set_deployment_status(self):
        """
            To change Field `pid` from -1 into this process's PID
        Returns: None
        """
        print("\n[%s] Updating PID information" % get_current_time())

        # Update Node information: `channel` and `pid`
        self.YOLOv3Service.update_node_information(self.node_id, self.pid)

    async def stop(self):
        print("\n[%s] Object Detection Service is going to stop" % get_current_time())
        
        # Delete Node
        self.YOLOv3Service.delete_node_information(self.node_id, self.pid)

        # exit the Object Detection Service
        exit()

    async def start(self):
        print("\n[%s] YOLOv3Handler try to consume the published data from [Scheduler Service]" % get_current_time())

        pid = os.getpid()
        print(" --- Object Detection Service's PID", pid)

        # Sample actions
        import time
        import signal
        for i in range(100):
            my_pid = os.getpid()
            print("## %s ## I am running, dude. >>> PID=" % i, my_pid)
            time.sleep(1)

            if i == 10:
                print(" >>> I AM KILLING MYSELF!!! pid=", pid)
                await self.stop()
                # os.kill(pid, signal.SIGTERM)  # or signal.SIGKILL
                # exit()

        channel = asab.Config["pubsub:channel"]["scheduler"]
        consumer = self.rc.pubsub()
        consumer.subscribe([channel])
        for item in consumer.listen():
            if isinstance(item["data"], int):
                pass
            else:
                # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
                config = pubsub_to_json(item["data"])

                # Input source handler: To ONLY allow one video stream once started
                if recognized_uri is None:
                    recognized_uri = config["uri"]

                # Run ONCE due to the current capability to capture only one video stream
                # TODO: To allow capturing multiple video streams (Future work)
                if not is_streaming:
                    is_streaming = True
                    t0_data = config["timestamp"]
                    t1_data = (time.time() - t0_data) * 1000
                    print('\n #### [%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_data))
                    # TODO: Saving latency for scheduler:consumer

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
