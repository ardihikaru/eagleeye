import asab
import logging
from .handler import ObjectDetectionHandler
from .soa.yolo_v3.app import YOLOv3
import requests
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_get
from enum import Enum

###

L = logging.getLogger(__name__)


###


class DetectionAlgorithmService(asab.Service):
    """
        Object Detection algorithm based on available object detection service
    """

    class AvailableDetectionAlgorithms(Enum):
        YOLOV3 = "YOLOv3"

    def __init__(self, app, service_name="detection.DetectionAlgorithmService"):
        super().__init__(app, service_name)
        self.app = app
        self.SubscriptionHandler = ObjectDetectionHandler(app)
        self.ResizerService = app.get_service("detection.ResizerService")

        # list of valid object detection algorithms
        self._valid_algorithms = frozenset([
            self.AvailableDetectionAlgorithms.YOLOV3.value
        ])

        # Set node alias
        redis = MyRedis(asab.Config)
        node_name = redis_get(redis.get_rc(), asab.Config["node"]["redis_name_key"])
        self.node_alias = "NODE-%s" % str(node_name)

        # Extractor service may not exist at this point
        # This variable will be set up in the init time
        # of ServiceAPIModule
        self.ZMQService = None

        # Build Object Detection config
        # TODO: To dynamically read the Object Detection version, if not found, Forced to close the Service!
        self._detection_algorithm = asab.Config["detection:config"]["algorithm"]
        self.detection = None

        # Get node information
        self.node_api_uri = asab.Config["eagleeye:api"]["node"]

    async def initialize(self, app):
        await self._init_object_detection_algorithm()

    async def _init_object_detection_algorithm(self):
        if self._detection_algorithm == self.AvailableDetectionAlgorithms.YOLOV3.value:
            # self.detection = self.YOLOv3Service
            self.detection = YOLOv3(asab.Config["objdet:yolo"])
        else:
            L.error("[ERROR] Subscription Failed; Reason: Method not implemented yet")
            await self.SubscriptionHandler.stop()

    async def start_subscription(self):
        try:
            L.warning("Configuring Object Detection")

            # validate algorithms
            if self._detection_algorithm not in self._valid_algorithms:
                L.error("[ERROR] Subscription Failed; Reason: Object Detection algorithm `{}` not recognized".
                        format(self._detection_algorithm))
                await self.SubscriptionHandler.stop()

            # await self._configure_object_detection()
            await self.SubscriptionHandler.set_configuration()
            await self.SubscriptionHandler.set_deployment_status()
            await self.SubscriptionHandler.start()
        except Exception as e:
            L.error("[ERROR] start_subscription: %s" % str(e))
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
            L.error("[ERROR]: %s" % str(e))
            return False, None, None, None

    async def update_node_information(self, node_id, pid):
        update_uri = self.node_api_uri + "/" + node_id

        # defining a params dict for the parameters to be sent to the API
        request_json = {
            # "pid": pid,
            "channel": "node-" + node_id
        }
        headers = {"Content-Type": "application/json"}

        # sending get request and saving the response as response object
        req = requests.put(url=update_uri, json=request_json, headers=headers)

        # extracting data in json format
        resp = req.json()

        if "status" in resp and resp["status"] != 200:
            await self.SubscriptionHandler.stop()

    async def detect_object(self, frame):
        # print("####[%s]##### START OBJECT DETECTION" % self.node_alias)
        L.warning("####[%s]##### START OBJECT DETECTION" % self.node_alias)
        bbox_data, det, names, pre_proc_lat, yolo_lat = None, None, None, None, None
        from_numpy_lat, image4yolo_lat, pred_lat = None, None, None
        try:
            # Perform conversion first!
            resized_frame, pre_proc_lat = await self.ResizerService.cpu_convert_to_padded_size(frame)
            # TODO: To add GPU-based downsample function

            # Perform object detection
            bbox_data, det, names, yolo_lat, from_numpy_lat, image4yolo_lat, pred_lat = \
                self.detection.get_detection_results(resized_frame, frame)

        except Exception as e:
            L.error("[ERROR]: %s" % str(e))
            await self.SubscriptionHandler.stop()

        # return bbox_data, det, names, pre_proc_lat, yolo_lat
        return bbox_data, det, names, pre_proc_lat, yolo_lat, from_numpy_lat, image4yolo_lat, pred_lat

    async def delete_node_information(self, node_id):
        delete_uri = self.node_api_uri + "/" + node_id
        req = requests.delete(url=delete_uri)
        resp = req.json()

        if "status" in resp and resp["status"] != 200:
            await self.SubscriptionHandler.stop()
