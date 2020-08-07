import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time, pubsub_to_json
from ext_lib.redis.translator import redis_get, redis_set
import os
from concurrent.futures import ThreadPoolExecutor
import time
# from multiprocessing import shared_memory
import numpy as np
import signal

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

        self.LatCollectorService = app.get_service("detection.LatencyCollectorService")

        # Default None
        self.node_name = int(asab.Config["node"]["name"])  # Should be an integer and unique, i.e. 1, 2, 3 ...
        self.node_id = asab.Config["node"]["id"]
        self.pid = os.getpid()
        self.node_alias = "NODE-%s" % asab.Config["node"]["name"]
        self.node_info = self._gen_node_info()
        self.node_info_list = self._dict2list(self.node_info)

        # Extra Module params
        self.cs_enabled = bool(int(asab.Config["node"]["candidate_selection"]))
        self.pv_enabled = bool(int(asab.Config["node"]["Persistence_validation"]))
        self.cv_out = bool(int(asab.Config["objdet:yolo"]["cv_out"]))

        # PiH Persistence Validation params
        self.total_pih_candidates = 0
        self.persistence_window = int(asab.Config["persistence_detection"]["persistence_window"])
        self.period_pih_candidates = []

    def _dict2list(self, dict_data):
        list_data = []
        for key, value in dict_data.items():
            tmp_list = [key, value]
            list_data.append(tmp_list)

        return np.asarray(list_data)

    def _gen_node_info(self):
        return {
            "id": asab.Config["node"]["name"],
            "name": int(asab.Config["node"]["name"]),
            "idle": asab.Config["node"]["idle"]
        }

    async def set_configuration(self):
        # Initialize YOLOv3 configuration
        print("\n[%s][%s] Initialize YOLOv3 configuration" % (get_current_time(), self.node_alias))

    async def set_deployment_status(self):
        """ To change Field `pid` from -1 into this process's PID """
        print("\n[%s][%s] Updating PID information" % (get_current_time(), self.node_alias))

        # Update Node information: `channel` and `pid`
        await self.DetectionAlgorithmService.update_node_information(self.node_id, self.pid)

        # Set ZMQ Receiver (& Sender) configuration
        # print("## # Set ZMQ Receiver (& Sender) configuration ##")
        await self.DetectionAlgorithmService.set_zmq_configurations(self.node_name, self.node_id)

    async def stop(self):
        print("\n[%s][%s] Object Detection Service is going to stop" % (get_current_time(), self.node_alias))

        # Delete Node
        # await self.DetectionAlgorithmService.delete_node_information(asab.Config["node"]["id"])
        await self.DetectionAlgorithmService.delete_node_information(self.node_id)

        # Kill PID !!!
        os.kill(self.pid, 9)
        # os.kill(self.pid, signal.SIGTERM)  # or signal.SIGKILL
        # os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)  # Send the signal to all the process groups

        # exit the Object Detection Service
        exit()

    def _set_idle_status(self, shm_nodes, snode_id, status):
        for i in range(len(shm_nodes[snode_id])):
            if shm_nodes[0][i][0] == "idle":
                shm_nodes[0][i][1] = status

    async def start(self):
        channel = "node-" + self.node_id
        print("\n[%s][%s] YOLOv3Handler try to subsscribe to channel `%s` from [Scheduler Service]" %
              (get_current_time(), self.node_alias, channel))

        # set params to store tmp latency data
        # latency = {
        #     "preproc": [],
        #     "yolo": [],
        #     "cand_selection": []
        # }

        # bug fix: invalid e2e latency due to detection issue with CPU
        # t_start = None

        # Set default value of shm node
        # shm_node = None
        redis_key = self.node_id + "_status"

        consumer = self.rc.pubsub()
        consumer.subscribe([channel])
        for item in consumer.listen():
            if isinstance(item["data"], int):
                print("\n[%s][%s] YOLOv3Handler start listening to [Scheduler Service]" %
                      (get_current_time(), self.node_alias))
            else:
                # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
                image_info = pubsub_to_json(item["data"])
                # print(" >>> image_info:", image_info)

                # # assign shm value: ONCE only
                # if shm_node is None:
                #     print("### MULAI ASSIGN SHM")
                #     # try:
                #     #     shm = shared_memory.SharedMemory(name=self.node_id)
                #     #     # shm_node = shared_memory.SharedMemory(name=self.node_id)
                #     #     shm_node = np.ndarray(self.node_info_list.shape, dtype=np.string, buffer=shm.buf)
                #     #     print(">>>>>> shm_node:", )
                #     # except Exception as e:
                #     #     print(">>>>>> e:", e)
                
                # print("********* shm_node:", shm_node)
                # print(">> > > > >> >START Receiving ZMQ in OBJDET @ ts:", time.time(), redis_get(self.rc, channel))

                # if not image_info["active"]:
                if redis_get(self.rc, channel) is not None:
                    self.rc.delete(channel)
                    print("\n[%s][%s] Forced to exit the Object Detection Service" %
                          (get_current_time(), self.node_alias))
                    await self.stop()
                    break

                # TODO: To start TCP Connection and be ready to capture the image from [Scheduler Service]
                # TODO: To have a tag as the image identifier, i.e. DroneID
                # TODO: To add a timeout, if no response found after a `timeout` time, ignore this (Future work)
                is_success, frame_id, t0_zmq, img = await self.DetectionAlgorithmService.get_img()
                # print(">>>> RECEIVED DATA:", is_success, frame_id, t0_zmq, img.shape)
                t1_zmq = (time.time() - t0_zmq) * 1000  # TODO: This is still INVALID! it got mixed up with Det latency!
                print('\n[%s] Latency for Receiving Image ZMQ (%.3f ms)' % (get_current_time(), t1_zmq))
                # TODO: To save latency into ElasticSearchDB (Future work)

                # BUG FIX: Start t0 e2e frame from here (later on, PLUS with `t1_zmq` latency)
                t0_e2e_latency = time.time()

                # Start performing object detection
                bbox_data, det, names, pre_proc_lat, yolo_lat = await self.DetectionAlgorithmService.detect_object(img)

                # build & submit latency data: Pre-processing
                await self._save_latency(frame_id, pre_proc_lat, "N/A", "preproc_det", "Pre-processing")

                # build & submit latency data: YOLO
                await self._save_latency(frame_id, yolo_lat, image_info["algorithm"], "detection", "Object Detection")

                # Get img information
                h, w, c = img.shape

                # Performing Candidate Selection Algorithm, if enabled
                if self.cs_enabled and det is not None:
                    print("***** [%s] Performing Candidate Selection Algorithm" % self.node_alias)
                    t0_cs = time.time()
                    mbbox_data = await self.CandidateSelectionService.calc_mbbox(bbox_data, det, names, h, w, c)
                    t1_cs = (time.time() - t0_cs) * 1000
                    print('\n[%s] Latency of Candidate Selection Algo. (%.3f ms)' % (get_current_time(), t1_cs))
                    # print(" >>>>> mbbox_data:", mbbox_data)

                    # build & submit latency data: PiH Candidate Selection
                    await self._save_latency(frame_id, t1_cs, "PiH Candidate Selection", "candidate_selection",
                                             "Extra Pipeline")

                    # Performing Persistence Validation Algorithm, if enabled
                    if self.pv_enabled and len(mbbox_data) > 0:
                        print("***** [%s] Performing Persistence Validation Algorithm" % self.node_alias)

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
                        print('\n[%s] Latency of Persistence Detection Algorithm (%.3f ms)' %
                              (get_current_time(), t1_pv))

                        # build & submit latency data: PiH Persistence Validation
                        await self._save_latency(frame_id, t1_pv, "PiH Persistence Validation", "persistence_validation",
                                                 "Extra Pipeline")
                    else:
                        # Set default label, in case PV algorithm is DISABLED
                        label = asab.Config["bbox_config"]["pih_label"]
                        det_status = label + " object FOUND"

                    print("\n[%s][%s]Frame-%s label=[%s], det_status=[%s]" %
                          (get_current_time(), self.node_alias, str(frame_id), label, det_status))

                # If enable visualizer, send the bbox into the Visualizer Service
                if self.cv_out:
                    print("\n[%s][%s] SENDING BBox INTO Visualizer Service!" % (get_current_time(), self.node_alias))

                # Set this node as available again
                redis_set(self.rc, redis_key, True)

                # Capture and store e2e latency
                t1_e2e_latency = (time.time() - t0_e2e_latency) * 1000
                t1_e2e_latency = t1_e2e_latency + t1_zmq
                # if t_start is None:
                #     t_start = time.time()
                # else:
                #     t1_e2e_latency = t1_e2e_latency - t_start
                #     t_start = t1_e2e_latency
                await self._store_e2e_latency(str(frame_id), t1_e2e_latency)

            print("\n[%s] Node-%s is ready to serve." % (get_current_time(), self.node_name))

        print("\n[%s][%s] YOLOv3Handler stopped listening to [Scheduler Service]" %
              (get_current_time(), self.node_alias))
        # Call stop function since it no longers listening
        await self.stop()

    async def _store_e2e_latency(self, frame_id, t1_e2e_latency):
        # t0_e2e_latency = await self._get_t0_e2e_latency(frame_id)  # BUG Calculation here!
        # t1_e2e_latency = (time.time() - t0_e2e_latency) * 1000
        # t1_e2e_latency = (t1_e2e_latency - t0_e2e_latency) * 1000
        print('[%s] E2E Latency of frame-%s (%.3f ms)' % (get_current_time(), frame_id, t1_e2e_latency))
        # TODO: TO save latency into ElasticSearchDB

        # build & submit latency data: E2E Latency
        await self._save_latency(frame_id, t1_e2e_latency, "N/A", "e2e_latency", "End-to-End",
                                 node_id=self.node_id, node_name=str(self.node_name))

    # TODO: To implement timeout!!!!!
    async def _get_t0_e2e_latency(self, frame_id):
        # get t0_e2e_latency from RedisDB
        e2e_lat_key = self.node_id + "-%s" % frame_id + "-e2e-latency"

        t0_e2e_waiting = time.time()
        while redis_get(self.rc, e2e_lat_key) is None:
            continue
        t1_e2e_waiting = (time.time() - t0_e2e_waiting) * 1000
        print('\n[%s] Latency for waiting redis key e2e latency (%.3f ms)' % (get_current_time(), t1_e2e_waiting))

        return redis_get(self.rc, e2e_lat_key)

    async def _save_latency(self, frame_id, latency, algorithm="[?]", section="[?]", cat="Object Detection",
                            node_id="-", node_name="-"):
        t0_preproc = time.time()
        preproc_latency_data = {
            "frame_id": int(frame_id),
            "category": cat,
            "algorithm": algorithm,
            "section": section,
            "latency": latency,
            "node_id": node_id,
            "node_name": node_name
        }
        # Submit and store latency data: Pre-processing
        if not await self.LatCollectorService.store_latency_data_thread(preproc_latency_data):
            await self.stop()
        t1_preproc = (time.time() - t0_preproc) * 1000
        print('\n[%s] Proc. Latency of %s (%.3f ms)' % (get_current_time(), section, t1_preproc))

    async def _maintaince_period_pih_cand(self):
        if len(self.period_pih_candidates) > self.persistence_window:
            self.period_pih_candidates.pop(0)
