import asab
import logging
from .handler import YOLOv3Handler
from ext_lib.utils import get_current_time
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
        node.delete_by_client(node_id)
