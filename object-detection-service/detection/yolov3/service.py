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
        await self.ZMQService.set_configurations(node_name, node_id)
        # node = Node()
        # node.update_data_by_id(node_id, {
        #     "pid": pid,
        #     "channel": "node-" + node_id
        # })
        
    # TODO: To tag each captured image and identify the sender (DroneID)
    async def get_img(self):
        try:
            # print("##### @ get_img ......")
            array_name, image = self.ZMQService.get_zmq_receiver().recv_image()
            tmp = array_name.split("-")
            frame_id = int(tmp[0])
            t0 = float(tmp[1])
            # array_name, image = self.ZMQService.get_zmq_receiver().recv_img()
            # print(">>> DISINI SIH ..")
            # print(" --- `Frame Data` has been successfully received >>> ", array_name, image.shape)

            # detection_status = self.__is_detection_finished()
            # if self.__is_detection_finished():
            # if detection_status:
            #     try:
            #         self.process_pih2image()
            #     except Exception as e:
            #         print("process pih2image GAGAL ...", e)
            #     print(" --- `Received Frame` data has been successfully processed & Plotted;")
                # self.send_to_visualizer()
            # elif detection_status is not None and not detection_status:  # send raw frame without any BBox
            #     self.send_to_visualizer(no_bbox=True)
            # print(" >>>>> EMBUH ...")
            return True, frame_id, t0, image
            # return True, array_name, image
            # return False, None, None

        except Exception as e:
            print("\tERROR:", e)
            return False, None, None, None

    async def update_node_information(self, node_id, pid):
        node = Node()
        node.update_data_by_id(node_id, {
            "pid": pid,
            "channel": "node-" + node_id
        })
    
    async def delete_node_information(self, node_id):
        node = Node()
        node.delete_data_by_id(node_id)
