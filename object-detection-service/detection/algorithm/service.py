import asab
import logging
from .handler import YOLOv3Handler
from detection.controllers.node.node import Node
from detection.algorithm.soa.yolo_v3.app import YOLOv3

###

L = logging.getLogger(__name__)


###


class AlgorithmService(asab.Service):
    """
        Object Detection algorithm based on YOLOv3
    """

    def __init__(self, app, service_name="detection.AlgorithmService"):
        super().__init__(app, service_name)
        self.app = app
        self.SubscriptionHandler = YOLOv3Handler(app)

        # Extractor service may not exist at this point
        # This variable will be set up in the init time
        # of ServiceAPIModule
        self.ZMQService = None

        # Build YOLO config
        # TODO: To dynamically read the YOLO Version, if not found, Forced to close the Service!
        self.yolo = None

    async def start_subscription(self):
        await self._configure_object_detection()
        await self.SubscriptionHandler.set_configuration()
        await self.SubscriptionHandler.set_deployment_status()
        await self.SubscriptionHandler.start()

    async def _configure_object_detection(self):
        try:
            self.yolo = YOLOv3(asab.Config["objdet:yolo"])
        except Exception as e:
            print(" >>>> e:", e)
            await self.SubscriptionHandler.stop()

    async def set_zmq_configurations(self, node_name, node_id):
        await self.ZMQService.set_configurations(node_name, node_id)

    # TODO: To tag each captured image and identify the sender (DroneID)
    async def get_img(self):
        try:
            array_name, image = self.ZMQService.get_zmq_receiver().recv_image()
            tmp = array_name.split("-")
            frame_id = int(tmp[0])
            t0 = float(tmp[1])
            return True, frame_id, t0, image

        except Exception as e:
            print("\tERROR:", e)
            return False, None, None, None

    async def update_node_information(self, node_id, pid):
        node = Node()
        node.update_data_by_id(node_id, {
            "pid": pid,
            "channel": "node-" + node_id
        })

    async def detect_object(self, frame):
        print("######### START OBJECT DETECTION")
        pass
    
    async def delete_node_information(self, node_id):
        node = Node()
        node.delete_data_by_id(node_id)
