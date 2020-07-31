import asab
import logging
from .handler import YOLOv3Handler
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

        # Extractor service may not exist at this point
        # This variable will be set up in the init time
        # of ServiceAPIModule
        self.ZMQService = None

    async def start_subscription(self):
        await self.SubscriptionHandler.set_configuration()
        await self.SubscriptionHandler.set_deployment_status()
        await self.SubscriptionHandler.start()

    # TODO: To implement the coding!
    async def set_zmq_configurations(self, node_name, node_id):
        self.ZMQService.set_configurations(node_name, node_id)
        # node = Node()
        # node.update_data_by_id(node_id, {
        #     "pid": pid,
        #     "channel": "node-" + node_id
        # })

    async def update_node_information(self, node_id, pid):
        node = Node()
        node.update_data_by_id(node_id, {
            "pid": pid,
            "channel": "node-" + node_id
        })
    
    async def delete_node_information(self, node_id):
        node = Node()
        node.delete_data_by_id(node_id)
