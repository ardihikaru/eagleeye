import asab
import logging
from .handler import YOLOv3Handler
from ext_lib.utils import get_current_time, pubsub_to_json
from detection.controllers.node.node import Node

###

L = logging.getLogger(__name__)


###


class YOLOv3Service(asab.Service):
    """
        Object Detection algorithm based on YOLOv3
    """

    def __init__(self, app, service_name="detection.YOLOv3Service"):
        super().__init__(app, service_name)
        self.app = app
        self.SubscriptionHandler = YOLOv3Handler(app)

    async def start_subscription(self):
        await self.SubscriptionHandler.set_configuration()
        await self.SubscriptionHandler.set_deployment_status()
        await self.SubscriptionHandler.start()

    async def update_node_information(self, node_id, pid):
        node = Node()
        node.update_data_by_id(node_id, {
            "pid": pid,
            "channel": "node-" + node_id
        })
    
    async def delete_node_information(self, node_id):
        node = Node()
        node.delete_data_by_id(node_id)

    # def app_killer_service(self, pool_name, node_id, pid, channel, rc):
    #     print(">>>> App Killer Service is deployed!")
    #     print(pool_name, node_id, pid, channel)
    #
    #     # import time
    #     # time.sleep(2)
    #
    #     consumer = rc.pubsub()
    #     consumer.subscribe([channel])
    #     for item in consumer.listen():
    #         if isinstance(item["data"], int):
    #             print(" >>>>>>> START LISTENING ...")
    #             pass
    #         else:
    #             # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
    #             stop_trigger_data = pubsub_to_json(item["data"])
    #             print(" >>>> stop_trigger_data MESSAGE:", stop_trigger_data)
    #             # Destroy key `node_id` in the RedisDB
    #             rc.delete(node_id)
    #
    #     print(" >>> Dude, I am killing myself after waiting for 2 seconds..")

        # exit()
        # # Destroy key `node_id` in the RedisDB
        # rc.delete(node_id)
