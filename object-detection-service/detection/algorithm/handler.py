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
        self.PersValService = app.get_service("detection.PersistenceValidationService")
        self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

        # Default None
        self.node_name = int(asab.Config["node"]["name"])  # Should be an integer and unique, i.e. 1, 2, 3 ...
        self.node_id = asab.Config["node"]["id"]
        self.pid = os.getpid()

        # Extra Module params
        self.cs_enabled = bool(int(asab.Config["node"]["candidate_selection"]))
        self.pv_enabled = bool(int(asab.Config["node"]["Persistence_validation"]))
        self.cv_out = bool(int(asab.Config["objdet:yolo"]["cv_out"]))

        # PiH Persistence Validation params
        self.total_pih_candidates = 0
        self.persistence_window = int(asab.Config["persistence_detection"]["persistence_window"])
        self.period_pih_candidates = []

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
        # await self.DetectionAlgorithmService.delete_node_information(asab.Config["node"]["id"])
        await self.DetectionAlgorithmService.delete_node_information(self.node_id)

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
                # TODO: To have a tag as the image identifier, i.e. DroneID
                is_success, frame_id, t0_zmq, img = await self.DetectionAlgorithmService.get_img()
                print(">>>> RECEIVED DATA:", is_success, frame_id, t0_zmq, img.shape)
                t1_zmq = (time.time() - t0_zmq) * 1000
                print('\n #### [%s] Latency for Receiving Image ZMQ (%.3f ms)' % (get_current_time(), t1_zmq))
                # TODO: To save latency into ElasticSearchDB (Future work)

                # Start performing object detection
                bbox_data, det, names = await self.DetectionAlgorithmService.detect_object(img)

                # Get img information
                h, w, c = img.shape

                # Performing Candidate Selection Algorithm, if enabled
                if self.cs_enabled and det is not None:
                    print("***** Performing Candidate Selection Algorithm")
                    t0_cs = time.time()
                    mbbox_data = await self.CandidateSelectionService.calc_mbbox(bbox_data, det, names, h, w, c)
                    t1_cs = (time.time() - t0_cs) * 1000
                    print('\n #### [%s] Latency of Candidate Selection Algo. (%.3f ms)' % (get_current_time(), t1_cs))
                    print(" >>>>> mbbox_data:", mbbox_data)

                    # Performing Persistence Validation Algorithm, if enabled
                    if self.pv_enabled and len(mbbox_data) > 0:
                        print("***** Performing Persistence Validation Algorithm")

                        # Increment PiH candidates
                        self.total_pih_candidates += 1
                        self.period_pih_candidates.append(int(frame_id))

                        # mbbox_data_pv = await self.PersValService.predict_mbbox(mbbox_data)
                        t0_pv = time.time()
                        label, det_status = await self.PersValService.validate_mbbox(frame_id,
                                                                                         self.total_pih_candidates,
                                                                                         self.period_pih_candidates)
                        await self._maintaince_period_pih_cand()
                        t1_pv = (time.time() - t0_pv) * 1000
                        print('\n #### [%s] Latency of Persistence Detection Algorithm (%.3f ms)' %
                              (get_current_time(), t1_pv))
                        print("########### label, det_status:", label, det_status)
                    else:
                        # Set default label, in case PV algorithm is DISABLED
                        label = asab.Config["bbox_config"]["pih_label"]
                        det_status = label + " object FOUND"

                # If enable visualizer, send the bbox into the Visualizer Service
                if self.cv_out:
                    print("**** SENDING BBox INTO Visualizer Service!")

        print("\n[%s] YOLOv3Handler stopped listening to [Scheduler Service]" % get_current_time())
        # Call stop function since it no longers listening
        await self.stop()

    async def _maintaince_period_pih_cand(self):
        if len(self.period_pih_candidates) > self.persistence_window:
            self.period_pih_candidates.pop(0)
