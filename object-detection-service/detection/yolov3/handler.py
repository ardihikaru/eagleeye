import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time, pubsub_to_json
import os
from concurrent.futures import ThreadPoolExecutor

###

L = logging.getLogger(__name__)


###

class YOLOv3Handler(MyRedis):

    def __init__(self, app):
        super().__init__(asab.Config)
        self.YOLOv3Service = app.get_service("detection.YOLOv3Service")
        self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

        # Default None
        self.node_name = int(asab.Config["node"]["name"])  # Should be an integer and unique, i.e. 1, 2, 3 ...
        self.node_id = asab.Config["node"]["id"]
        self.pid = os.getpid()

    async def set_configuration(self):
        # Initialize YOLOv3 configuration
        print("\n[%s] Initialize YOLOv3 configuration" % get_current_time())

    async def set_deployment_status(self):
        """
            To change Field `pid` from -1 into this process's PID
        Returns: None
        """
        print("\n[%s] Updating PID information" % get_current_time())

        # Update Node information: `channel` and `pid`
        await self.YOLOv3Service.update_node_information(self.node_id, self.pid)

        # Set ZMQ Receiver (& Sender) configuration
        print("## # Set ZMQ Receiver (& Sender) configuration ##")
        await self.YOLOv3Service.set_zmq_configurations(self.node_name, self.node_id)

    async def _stop(self):
        print("\n[%s] Object Detection Service is going to stop" % get_current_time())
        
        # Delete Node
        await self.YOLOv3Service.delete_node_information(self.node_id)

        # exit the Object Detection Service
        exit()

    async def start(self):
        channel = "node-" + self.node_id
        print("\n[%s] YOLOv3Handler try to subsscribe to channel `%s` from [Scheduler Service]" %
              (get_current_time(), channel))

        # set ZMQ Frame Receiver

        consumer = self.rc.pubsub()
        consumer.subscribe([channel])
        for item in consumer.listen():
            if isinstance(item["data"], int):
                print("\n[%s] YOLOv3Handler start listening to [Scheduler Service]" % get_current_time())
            else:
                # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
                image_info = pubsub_to_json(item["data"])
                print(" >>> image_info:", image_info)

                import time
                print(">> > > > >> >START Receiving ZMQ in OBJDET @ ts:", time.time())

                # TODO: if the image_info's key `active`=False, BREAK the Pub/sub listener!
                if not image_info["active"]:
                    break

                # TODO: To start TCP Connection and be ready to capture the image from [Scheduler Service]
                print(" ###### I AM DOING SOMETHING HERE")
                while True:
                    is_success, frame_id, t0_zmq, img = await self.YOLOv3Service.get_img()
                    print(">>>> RECEIVED DATA:", is_success, frame_id, t0_zmq, img.shape)
                    t1_zmq = (time.time() - t0_zmq) * 1000
                    print('\n #### [%s] Latency for Receiving Image ZMQ (%.3f ms)' % (get_current_time(), t1_zmq))
                    # TODO: To save latency into ElasticSearchDB (Future work)

                    # print(" >>>> DISINI >>>> ", is_success, img.shape)
                    break

                # try:
                #     _, self.raw_image = self.frame_receiver.recv_image()
                #     print(" --- `Frame Data` has been successfully received: -- self.drone_id=", self.drone_id)
                # except Exception as e:
                #     print("\t\tRetrieve frame-%d ERROR:" % self.frame_id, e)

        print("\n[%s] YOLOv3Handler stopped listening to [Scheduler Service]" % get_current_time())
        # Call stop function since it no longers listening
        await self._stop()
