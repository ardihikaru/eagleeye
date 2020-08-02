import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time, pubsub_to_json
from ext_lib.redis.translator import redis_get
import os
from concurrent.futures import ThreadPoolExecutor

###

L = logging.getLogger(__name__)


###

class YOLOv3Handler(MyRedis):

    def __init__(self, app):
        super().__init__(asab.Config)
        self.DetectionAlgorithmService = app.get_service("detection.DetectionAlgorithmService")
        self.CandidateSelectionService = app.get_service("detection.CandidateSelectionService")
        self.PersistenceValidationService = app.get_service("detection.PersistenceValidationService")
        self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

        # Default None
        self.node_name = int(asab.Config["node"]["name"])  # Should be an integer and unique, i.e. 1, 2, 3 ...
        self.node_id = asab.Config["node"]["id"]
        self.pid = os.getpid()

        # Extra Module params
        self.cs_enabled = bool(int(asab.Config["node"]["candidate_selection"]))
        self.pv_enabled = bool(int(asab.Config["node"]["Persistence_validation"]))
        self.cv_out = bool(int(asab.Config["objdet:yolo"]["cv_out"]))

    async def set_configuration(self):
        # Initialize YOLOv3 configuration
        print("\n[%s] Initialize YOLOv3 configuration" % get_current_time())

    async def set_deployment_status(self):
        """ To change Field `pid` from -1 into this process's PID """
        print("\n[%s] Updating PID information" % get_current_time())

        # Update Node information: `channel` and `pid`
        await self.DetectionAlgorithmService.update_node_information(self.node_id, self.pid)

        # Set ZMQ Receiver (& Sender) configuration
        print("## # Set ZMQ Receiver (& Sender) configuration ##")
        await self.DetectionAlgorithmService.set_zmq_configurations(self.node_name, self.node_id)

    async def stop(self):
        print("\n[%s] Object Detection Service is going to stop" % get_current_time())

        # Delete Node
        await self.DetectionAlgorithmService.delete_node_information(asab.Config["node"]["id"])

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
                print(">> > > > >> >START Receiving ZMQ in OBJDET @ ts:", time.time(), redis_get(self.rc, channel))

                # if not image_info["active"]:
                if redis_get(self.rc, channel) is not None:
                    self.rc.delete(channel)
                    print(">>>>>>>>>>>>>>>> ####### STOPPING COY ....")
                    await self.stop()
                    break

                # TODO: To start TCP Connection and be ready to capture the image from [Scheduler Service]
                print(" ###### I AM DOING SOMETHING HERE")
                # while True:
                # TODO: To have a tag as the image identifier, i.e. DroneID
                is_success, frame_id, t0_zmq, img = await self.DetectionAlgorithmService.get_img()
                print(">>>> RECEIVED DATA:", is_success, frame_id, t0_zmq, img.shape)
                t1_zmq = (time.time() - t0_zmq) * 1000
                print('\n #### [%s] Latency for Receiving Image ZMQ (%.3f ms)' % (get_current_time(), t1_zmq))
                # TODO: To save latency into ElasticSearchDB (Future work)

                # Start performing object detection
                bbox_data = await self.DetectionAlgorithmService.detect_object(img)

                try:
                    # Performing Candidate Selection Algorithm, if enabled
                    if self.cs_enabled:
                        print("***** Performing Candidate Selection Algorithm")
                        mbbox_data = await self.CandidateSelectionService.calc_mbbox(bbox_data)

                        # Performing Persistence Validation Algorithm, if enabled
                        if self.pv_enabled:
                            print("***** Performing Persistence Validation Algorithm")
                            mbbox_data = await self.PersistenceValidationService.predict_mbbox(mbbox_data)
                except Exception as e:
                    print(" *** WAOW e:", e)

                # If enable visualizer, send the bbox into the Visualizer Service
                if self.cv_out:
                    print("**** SENDING BBox INTO Visualizer Service!")

        print("\n[%s] YOLOv3Handler stopped listening to [Scheduler Service]" % get_current_time())
        # Call stop function since it no longers listening
        await self.stop()
