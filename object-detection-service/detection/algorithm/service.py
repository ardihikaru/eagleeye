import asab
import logging
from .handler import YOLOv3Handler
from detection.algorithm.soa.yolo_v3.app import YOLOv3
import requests
import time
from ext_lib.utils import get_current_time

###

L = logging.getLogger(__name__)


###


class DetectionAlgorithmService(asab.Service):
    """
        Object Detection algorithm based on YOLOv3
    """

    def __init__(self, app, service_name="detection.DetectionAlgorithmService"):
        super().__init__(app, service_name)
        self.app = app
        self.SubscriptionHandler = YOLOv3Handler(app)
        self.ResizerService = app.get_service("detection.ResizerService")

        self.node_alias = "NODE-%s" % asab.Config["node"]["name"]

        # Extractor service may not exist at this point
        # This variable will be set up in the init time
        # of ServiceAPIModule
        self.ZMQService = None

        # Build YOLO config
        # TODO: To dynamically read the YOLO Version, if not found, Forced to close the Service!
        self.yolo = None

        # Get node information
        self.node_api_uri = asab.Config["eagleeye:api"]["node"]

    async def start_subscription(self):
        try:
            await self._configure_object_detection()
            await self.SubscriptionHandler.set_configuration()
            await self.SubscriptionHandler.set_deployment_status()
            await self.SubscriptionHandler.start()
        except Exception as e:
            # print(" >>>> start_subscription e:", e)
            L.error("[ERROR] start_subscription: %s" % str(e))
            await self.SubscriptionHandler.stop()

    async def _configure_object_detection(self):
        self.yolo = YOLOv3(asab.Config["objdet:yolo"])

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
            # print("\tERROR:", e)
            L.error("[ERROR]: %s" % str(e))
            return False, None, None, None

    async def update_node_information(self, node_id, pid):
        update_uri = self.node_api_uri + "/" + node_id

        # defining a params dict for the parameters to be sent to the API
        request_json = {
            "pid": pid,
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
        try:
            # Perform conversion first!
            # resized_frame = await self.ResizerService.cpu_convert_to_padded_size(frame)
            resized_frame, pre_proc_lat = await self.ResizerService.cpu_convert_to_padded_size(frame)
            # TODO: To add GPU-based downsample function
            # resized_frame = await self.ResizerService.gpu_convert_to_padded_size(frame)

            # # build latency data: Pre-processing
            # t0_preproc = time.time()
            # preproc_latency_data = {
            #     "frame_id": int(frame_id),
            #     "category": "Object Detection",
            #     "algorithm": algorithm,
            #     "section": "Pre-processing",
            #     "latency": pre_proc_lat
            # }
            # # Submit and store latency data: Pre-processing
            # if not await self.LatCollectorService.store_latency_data_thread(preproc_latency_data):
            #     await self.SubscriptionHandler.stop()
            # t1_preproc = (time.time() - t0_preproc) * 1000
            # print('\n[%s] Proc. Latency of Pre-processing (%.3f ms)' % (get_current_time(), t1_preproc))

            # Perform object detection
            bbox_data, det, names, yolo_lat = self.yolo.get_detection_results(resized_frame)
            # bbox_data = self.yolo.get_bbox_data(frame, False)

            # # build latency data: YOLO
            # t0_preproc = time.time()
            # preproc_latency_data = {
            #     "frame_id": int(frame_id),
            #     "category": "Object Detection",
            #     "algorithm": algorithm,
            #     "section": "YOLO",
            #     "latency": yolo_lat
            # }
            # # Submit and store latency data: YOLO
            # if not await self.LatCollectorService.store_latency_data_thread(preproc_latency_data):
            #     await self.SubscriptionHandler.stop()
            # t1_preproc = (time.time() - t0_preproc) * 1000
            # print('\n[%s] Proc. Latency of YOLO (%.3f ms)' % (get_current_time(), t1_preproc))

        except Exception as e:
            # print(" >>>> GET BBox e:", e)
            L.error("[ERROR]: %s" % str(e))
            await self.SubscriptionHandler.stop()
        return bbox_data, det, names, pre_proc_lat, yolo_lat

    async def delete_node_information(self, node_id):
        delete_uri = self.node_api_uri + "/" + node_id
        req = requests.delete(url=delete_uri)
        resp = req.json()

        if "status" in resp and resp["status"] != 200:
            await self.SubscriptionHandler.stop()
