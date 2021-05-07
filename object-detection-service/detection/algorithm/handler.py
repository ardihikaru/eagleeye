import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time, pubsub_to_json
from ext_lib.redis.translator import redis_get, redis_set
import os
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np
import simplejson as json
from ext_lib.commons.opencv_helpers import get_det_xyxy, torch2list_det
import aiohttp
import simplejson as json

###

L = logging.getLogger(__name__)


###

class ObjectDetectionHandler(MyRedis):

    def __init__(self, app):
        super().__init__(asab.Config)
        self.DetectionAlgorithmService = app.get_service("detection.DetectionAlgorithmService")
        self.CandidateSelectionService = app.get_service("detection.CandidateSelectionService")
        self.PersValService = app.get_service("detection.PersistenceValidationService")
        self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

        self.LatCollectorService = app.get_service("detection.LatencyCollectorService")
        self.GPSCollectorService = app.get_service("detection.GPSCollectorService")

        # Set node information
        self.node_name = redis_get(self.rc, asab.Config["node"]["redis_name_key"])
        self.node_id = redis_get(self.rc, asab.Config["node"]["redis_id_key"])

        self.pid = os.getpid()
        self.node_alias = "NODE-%s" % str(self.node_name)
        self.node_info = self._gen_node_info()
        self.node_info_list = self._dict2list(self.node_info)

        # Extra Module params
        self.cs_enabled = redis_get(self.rc, asab.Config["node"]["redis_pcs_key"])
        self.pv_enabled = redis_get(self.rc, asab.Config["node"]["redis_pv_key"])
        self.cv_out = bool(int(asab.Config["objdet:yolo"]["cv_out"]))

        # PiH Candidate Selection params
        self.pcs_is_microservice = asab.Config["pih_candidate_selection"].getboolean("is_microservice")
        self.pv_is_microservice = asab.Config["persistence_detection"].getboolean("is_microservice")

        # PiH Persistence Validation params
        self.total_pih_candidates = 0
        self.persistence_window = int(asab.Config["persistence_detection"]["persistence_window"])
        self.period_pih_candidates = []

        # save last selected_pairs in this node
        self._selected_pairs = None

        # private rest APIs
        self.pcs_url = asab.Config["pcs:api"]["url"]
        self.pv_url = asab.Config["pv:api"]["url"]

    def _dict2list(self, dict_data):
        list_data = []
        for key, value in dict_data.items():
            tmp_list = [key, value]
            list_data.append(tmp_list)

        return np.asarray(list_data)

    def _gen_node_info(self):
        return {
            "id": self.node_id,
            "name": int(self.node_name)
            # "idle": asab.Config["node"]["idle"]
        }

    async def set_configuration(self):
        # Initialize YOLOv3 configuration
        L.warning("\n[%s][%s] Initialize YOLOv3 configuration" % (get_current_time(), self.node_alias))

    async def set_deployment_status(self):
        """ To change Field `pid` from -1 into this process's PID """
        L.warning("\n[%s][%s] Updating PID information" % (get_current_time(), self.node_alias))

        # Update Node information: `channel` and `pid`
        await self.DetectionAlgorithmService.update_node_information(self.node_id, self.pid)

        # Set ZMQ Receiver (& Sender) configuration
        await self.DetectionAlgorithmService.set_zmq_configurations(self.node_name, self.node_id)

    async def stop(self):
        # print("\n[%s][%s] Object Detection Service is going to stop" % (get_current_time(), self.node_alias))
        L.warning("\n[%s][%s] Object Detection Service is going to stop" % (get_current_time(), self.node_alias))

        # Delete Node
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

    async def send_pcs_request(self, bbox_data, list_det, names, h, w, c, selected_pairs):
        request_json = {
            "bbox_data": bbox_data,
            "det": list_det,
            "names": names,
            "h": h,
            "w": w,
            "c": c,
            "selected_pairs": selected_pairs,
        }

        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.post(
                    self.pcs_url,
                    data=json.dumps(request_json)
                )

                if resp.status != 200:
                    L.error("Can't get a proper response. Server responded with code '{}':\n{}".format(
                        resp.status,
                        await resp.text()
                    ))
                    return [], []
                else:
                    r = await resp.json()
                    resp_json = r.get("data")
                    return resp_json.get("mbbox_data", []), resp_json.get("selected_pairs", [])
        except Exception as e:
            L.error("[PCS ERROR] `{}`".format(e))
            return [], []

    async def send_pv_request(self, frame_id, total_pih_candidates, period_pih_candidates):
        request_json = {
            "frame_id": frame_id,
            "total_pih_candidates": total_pih_candidates,
            "period_pih_candidates": period_pih_candidates,
        }

        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.post(
                    self.pv_url,
                    data=json.dumps(request_json)
                )

                if resp.status != 200:
                    L.error("Can't get a proper response. Server responded with code '{}':\n{}".format(
                        resp.status,
                        await resp.text()
                    ))
                    return [], []
                else:
                    r = await resp.json()
                    resp_json = r.get("data")
                    return resp_json.get("mbbox_data", []), resp_json.get("selected_pairs", [])
        except Exception as e:
            L.error("[PV ERROR] `{}`".format(e))
            return [], []

    async def _save_detection_related_latency(self, pre_proc_lat, yolo_lat, from_numpy_lat,
                                                         image4yolo_lat, pred_lat):
        # build & submit latency data: Pre-processing
        L.warning("build & submit latency data: Pre-processing")
        await self._save_latency(frame_id, pre_proc_lat, "N/A", "preproc_det", "Pre-processing")

        # build & submit latency data: YOLO
        L.warning("build & submit latency data: YOLO")
        await self._save_latency(frame_id, yolo_lat, image_info["algorithm"], "detection", "Object Detection")

        # save other proc. latency
        await self._save_latency(frame_id, from_numpy_lat, image_info["algorithm"], "detection", "from_numpy")
        await self._save_latency(frame_id, image4yolo_lat, image_info["algorithm"], "detection", "image4yolo")
        await self._save_latency(frame_id, pred_lat, image_info["algorithm"], "detection", "pred")

    async def _exec_extra_pipeline(self, img, bbox_data, mbbox_data, plot_info):
        # Get img information
        h, w, c = img.shape

        # Performing Candidate Selection Algorithm, if enabled
        L.warning("Performing Candidate Selection Algorithm, if enabled")
        if self.cs_enabled and det is not None:
            # print("***** [%s] Performing Candidate Selection Algorithm" % self.node_alias)
            L.warning("***** [%s] Performing Candidate Selection Algorithm" % self.node_alias)
            t0_cs = time.time()

            # convert torch `det` into list `det`
            list_det = torch2list_det(det)

            if self.pcs_is_microservice:
                mbbox_data, self._selected_pairs = await self.send_pcs_request(
                    bbox_data, list_det, names, h, w, c, self._selected_pairs
                )
            else:
                mbbox_data, self._selected_pairs = await self.CandidateSelectionService.calc_mbbox(
                    bbox_data, det, names, h, w, c, self._selected_pairs
                )

            t1_cs = (time.time() - t0_cs) * 1000
            # print('\n[%s] Latency of Candidate Selection Algo. (%.3f ms)' % (get_current_time(), t1_cs))
            L.warning('\n[%s] Latency of Candidate Selection Algo. (%.3f ms)' % (get_current_time(), t1_cs))

            # build & submit latency data: PiH Candidate Selection
            await self._save_latency(frame_id, t1_cs, "PiH Candidate Selection", "candidate_selection",
                                     "Extra Pipeline")

            # Performing Persistence Validation Algorithm, if enabled
            if self.pv_enabled and len(mbbox_data) > 0:
                # print("***** [%s] Performing Persistence Validation Algorithm" % self.node_alias)
                L.warning("***** [%s] Performing Persistence Validation Algorithm" % self.node_alias)

                # Increment PiH candidates
                self.total_pih_candidates += 1
                self.period_pih_candidates.append(int(frame_id))

                # mbbox_data_pv = await self.PersValService.predict_mbbox(mbbox_data)
                t0_pv = time.time()

                if self.pv_is_microservice:
                    label, det_status = await self.send_pv_request(
                        frame_id,
                        self.total_pih_candidates,
                        self.period_pih_candidates
                    )
                else:
                    label, det_status = await self.PersValService.validate_mbbox(
                        frame_id,
                        self.total_pih_candidates,
                        self.period_pih_candidates
                    )

                await self._maintaince_period_pih_cand()
                t1_pv = (time.time() - t0_pv) * 1000
                # print('\n[%s] Latency of Persistence Detection Algorithm (%.3f ms)' %
                #       (get_current_time(), t1_pv))
                L.warning('\n[%s] Latency of Persistence Detection Algorithm (%.3f ms)' %
                          (get_current_time(), t1_pv))

                # build & submit latency data: PiH Persistence Validation
                await self._save_latency(frame_id, t1_pv, "PiH Persistence Validation", "persistence_validation",
                                         "Extra Pipeline")
            else:
                # Set default label, in case PV algorithm is DISABLED
                label = asab.Config["bbox_config"]["pih_label"]
                det_status = label + " object FOUND"

            # If MBBox data available, build plot_info
            if len(mbbox_data) > 0:

                color = asab.Config["bbox_config"]["pih_color"].strip('][').split(', ')
                for i in range(len(color)):
                    color[i] = int(color[i])

                # collect latest GPS Data
                gps_data = await self.GPSCollectorService.get_gps_data()

                plot_info = {
                    "bbox": bbox_data,
                    "mbbox": mbbox_data,
                    "color": color,
                    "label": label,
                    "gps_data": gps_data
                }

            L.warning("\n[%s][%s]Frame-%s label=[%s], det_status=[%s]" %
                      (get_current_time(), self.node_alias, str(frame_id), label, det_status))

        return mbbox_data, plot_info

    async def start(self):
        channel = "node-" + self.node_id
        L.warning("\n[%s][%s] YOLOv3Handler try to subsscribe to channel `%s` from [Scheduler Service]" %
              (get_current_time(), self.node_alias, channel))

        redis_key = self.node_id + "_status"

        consumer = self.rc.pubsub()
        consumer.subscribe([channel])
        for item in consumer.listen():
            if isinstance(item["data"], int):
                # print("\n[%s][%s] YOLOv3Handler start listening to [Scheduler Service]" %
                #       (get_current_time(), self.node_alias))
                L.warning("\n[%s][%s] YOLOv3Handler start listening to [Scheduler Service]" %
                      (get_current_time(), self.node_alias))
            else:
                # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
                """
                Sender: 
                
                Previous data:
                {
                    'active': True, 
                    'algorithm': 'YOLOv3', 
                    'ts': 1620022172.6399865
                }
                
                New data:
                {
                    'active': True, 
                    'algorithm': 'YOLOv3', 
                    'ts': 1620022172.6399865,
                    'drone_id': 1,
                }
                """
                image_info = pubsub_to_json(item["data"])
                L.warning("Collecting Image Info")
                L.warning(json.dumps(image_info))
                L.warning("Image INFORMATION is collected.")

                if redis_get(self.rc, channel) is not None:
                    self.rc.delete(channel)
                    L.warning("\n[%s][%s] Forced to exit the Object Detection Service" %
                          (get_current_time(), self.node_alias))
                    await self.stop()
                    break

                # TODO: To start TCP Connection and be ready to capture the image from [Scheduler Service]
                # TODO: To have a tag as the image identifier, i.e. DroneID
                # TODO: To add a timeout, if no response found after a `timeout` time, ignore this (Future work)
                L.warning("Try to collect Image DATA.")
                is_success, frame_id, t0_zmq, img = await self.DetectionAlgorithmService.get_img()
                L.warning("Receiving image data via ZMQ (is_success=%s; frame_id=%s)" % (str(is_success), str(frame_id)))
                L.warning("Image DATA is collected.")
                # print(">>>> RECEIVED DATA:", is_success, frame_id, t0_zmq, img.shape)
                t1_zmq = (time.time() - t0_zmq) * 1000  # TODO: This is still INVALID! it got mixed up with Det latency!
                # print('\n[%s] Latency for Receiving Image ZMQ (%.3f ms)' % (get_current_time(), t1_zmq))
                L.warning('\n[%s] Latency for Receiving Image ZMQ (%.3f ms)' % (get_current_time(), t1_zmq))
                # TODO: To save latency into ElasticSearchDB (Future work)

                # BUG FIX: Start t0 e2e frame from here (later on, PLUS with `t1_zmq` latency)
                t0_e2e_latency = time.time()

                # Start performing object detection
                L.warning("Start performing object detection")
                # bbox_data, det, names, (tdiff_inference + tdiff_nms), tdiff_from_numpy, tdiff_image4yolo, tdiff_pred
                #  bbox_data, det, names, yolo_lat, from_numpy_lat, image4yolo_lat, pred_lat
                bbox_data, det, names, pre_proc_lat, yolo_lat, from_numpy_lat, image4yolo_lat, pred_lat = \
                    await self.DetectionAlgorithmService.detect_object(img)

                # Set default `mbbox_data` and `plot_info` values
                mbbox_data = []
                plot_info = {}
                if len(bbox_data) > 0:  # detected objects
                    # save latecny
                    await self._save_detection_related_latency(pre_proc_lat, yolo_lat, from_numpy_lat,
                                                         image4yolo_lat, pred_lat)
                    # execute PiH Candidate Selection & PiH Persitance Validation
                    mbbox_data, plot_info = await self._exec_extra_pipeline(img, bbox_data, mbbox_data, plot_info)

                    # If enable visualizer, send the bbox into the Visualizer Service
                    if self.cv_out:
                        L.warning("\n[%s][%s][%s] Store Box INTO Visualizer Service!" %
                                  (get_current_time(), self.node_alias, str(frame_id)))
                        t0_plotinfo_saving = time.time()
                        drone_id = asab.Config["stream:config"]["drone_id"]
                        plot_info_key = "plotinfo-drone-%s-frame-%s" % (drone_id, str(frame_id))
                        redis_set(self.rc, plot_info_key, plot_info, expired=10)  # delete value after 10 seconds
                        t1_plotinfo_saving = (time.time() - t0_plotinfo_saving) * 1000
                        L.warning('\n[%s] Latency of Storing Plot info in redisDB (%.3f ms)' %
                                  (get_current_time(), t1_plotinfo_saving))

                # Else, No object detected!
                else:
                    L.warning("[DETECTION_RESULT] Unable to detect any valid objects in frame-{}".format(frame_id))

                # Set this node as available again
                redis_set(self.rc, redis_key, True)
                L.warning("[DOD_DEBUG] Status of this Node: %s" % str(redis_get(self.rc, redis_key)))

                # Capture and store e2e latency
                t1_e2e_latency = (time.time() - t0_e2e_latency) * 1000
                t1_e2e_latency = t1_e2e_latency + t1_zmq
                # if t_start is None:
                #     t_start = time.time()
                # else:
                #     t1_e2e_latency = t1_e2e_latency - t_start
                #     t_start = t1_e2e_latency
                await self._store_e2e_latency(str(frame_id), t1_e2e_latency)

            # print("\n[%s] Node-%s is ready to serve." % (get_current_time(), self.node_name))
            L.warning("\n[%s] Node-%s is ready to serve." % (get_current_time(), self.node_name))

        # print("\n[%s][%s] YOLOv3Handler stopped listening to [Scheduler Service]" %
        #       (get_current_time(), self.node_alias))
        L.warning("\n[%s][%s] YOLOv3Handler stopped listening to [Scheduler Service]" %
              (get_current_time(), self.node_alias))
        # Call stop function since it no longers listening
        await self.stop()

    async def _store_e2e_latency(self, frame_id, t1_e2e_latency):
        # t0_e2e_latency = await self._get_t0_e2e_latency(frame_id)  # BUG Calculation here!
        # t1_e2e_latency = (time.time() - t0_e2e_latency) * 1000
        # t1_e2e_latency = (t1_e2e_latency - t0_e2e_latency) * 1000
        # print('[%s] E2E Latency of frame-%s (%.3f ms)' % (get_current_time(), frame_id, t1_e2e_latency))
        L.warning('[%s] E2E Latency of frame-%s (%.3f ms)' % (get_current_time(), frame_id, t1_e2e_latency))
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
        # print('\n[%s] Latency for waiting redis key e2e latency (%.3f ms)' % (get_current_time(), t1_e2e_waiting))
        L.warning('\n[%s] Latency for waiting redis key e2e latency (%.3f ms)' % (get_current_time(), t1_e2e_waiting))

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
        # print('\n[%s] Proc. Latency of %s (%.3f ms)' % (get_current_time(), section, t1_preproc))
        L.warning('\n[%s] Proc. Latency of %s (%.3f ms)' % (get_current_time(), section, t1_preproc))

    async def _maintaince_period_pih_cand(self):
        if len(self.period_pih_candidates) > self.persistence_window:
            self.period_pih_candidates.pop(0)
