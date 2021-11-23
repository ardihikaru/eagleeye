import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time, pubsub_to_json
from ext_lib.redis.translator import redis_get, redis_set, pub
import os
from concurrent.futures import ThreadPoolExecutor
import time
from enum import Enum
import numpy as np
import simplejson as json
from ext_lib.commons.opencv_helpers import get_det_xyxy, torch2list_det
import aiohttp
from asab import LOG_NOTICE
import cv2

###

L = logging.getLogger(__name__)


###

class ObjectDetectionHandler(MyRedis):

	class VizCommunicationMode(Enum):
		DIRECT = "direct"
		SORTER = "sorter"

	def __init__(self, app):
		super().__init__(asab.Config)
		self.ResizerService = app.get_service("detection.ResizerService")
		self.DetectionAlgorithmService = app.get_service("detection.DetectionAlgorithmService")
		self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

		self.lat_collector_svc = app.get_service("eagleeye.LatencyCollectorService")
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

		# private rest APIs
		self.pcs_url = asab.Config["pcs:api"]["url"]

		# sorter config
		self.ch_prefix = asab.Config["sorter"]["ch_prefix"]
		self.viz_com_mode = asab.Config["visualizer"]["viz_com_mode"]

		self.compressed_img = asab.Config["image:preprocessing"].getboolean("compressed_img")

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
		L.log(LOG_NOTICE, "[{}][{}] Initialize YOLOv3 configuration".format(get_current_time(), self.node_alias))

	async def set_deployment_status(self):
		""" To change Field `pid` from -1 into this process's PID """
		L.log(LOG_NOTICE, "[{}][{}] Updating PID information".format(get_current_time(), self.node_alias))

		# Update Node information: `channel` and `pid`
		await self.DetectionAlgorithmService.update_node_information(self.node_id, self.pid)

		# Set ZMQ Receiver (& Sender) configuration
		await self.DetectionAlgorithmService.set_zmq_configurations(self.node_name, self.node_id)

	async def stop(self):
		L.log(LOG_NOTICE, "[{}][{}] Object Detection Service is going to stop".format(get_current_time(), self.node_alias))

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

	async def send_pcs_request(self, drone_id, bbox_data, list_det, names, h, w, c):
		request_json = {
			"drone_id": str(drone_id),
			"bbox_data": bbox_data,
			"det": list_det,
			"names": names,
			"h": h,
			"w": w,
			"c": c,
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
					return []
				else:
					r = await resp.json()
					resp_json = r.get("data")
					return resp_json.get("mbbox_data", [])
		except Exception as e:
			L.error("[PCS ERROR] `{}`".format(e))
			return []

	async def _save_detection_related_latency(self, pre_proc_lat, yolo_lat, from_numpy_lat,
											  image4yolo_lat, pred_lat, frame_id, image_info, img_resizer_lat):
		# build & submit latency data: Pre-processing
		L.log(LOG_NOTICE, "build & submit latency data: Pre-processing")
		await self._save_latency(frame_id, pre_proc_lat, "N/A", "preproc_det", "Pre-processing")

		# build & submit latency data: YOLO
		L.log(LOG_NOTICE, "build & submit latency data: YOLO")
		await self._save_latency(frame_id, yolo_lat, image_info["algorithm"], "detection", "Object Detection",
								 node_id=str(self.node_id), node_name=str(self.node_name))

		# save other proc. latency
		await self._save_latency(frame_id, from_numpy_lat, image_info["algorithm"], "detection", "from_numpy",
								 node_id=str(self.node_id), node_name=str(self.node_name))
		await self._save_latency(frame_id, image4yolo_lat, image_info["algorithm"], "detection", "image4yolo",
								 node_id=str(self.node_id), node_name=str(self.node_name))
		await self._save_latency(frame_id, pred_lat, image_info["algorithm"], "detection", "pred",
								 node_id=str(self.node_id), node_name=str(self.node_name))
		await self._save_latency(frame_id, img_resizer_lat, "", "preproc", "img_scaling",
								 node_id=str(self.node_id), node_name=str(self.node_name))

	async def _exec_extra_pipeline(self, img, bbox_data, mbbox_data, plot_info, det, names, frame_id, drone_id):
		# Get img information
		h, w, c = img.shape

		# Performing Candidate Selection Algorithm, if enabled
		L.log(LOG_NOTICE, "Performing Candidate Selection Algorithm, if enabled")
		if self.cs_enabled and det is not None:
			L.log(LOG_NOTICE, "***** [%s] Performing Candidate Selection Algorithm" % self.node_alias)
			t0_cs = time.time()

			# convert torch `det` into list `det`
			list_det = torch2list_det(det)

			mbbox_data = await self.send_pcs_request(
				drone_id, bbox_data, list_det, names, h, w, c
			)

			t1_cs = (time.time() - t0_cs) * 1000
			L.log(LOG_NOTICE, '[{}] Latency of Candidate Selection Algo. (%.3f ms)'.format(get_current_time()) % (t1_cs))

			# build & submit latency data: PiH Candidate Selection
			await self._save_latency(frame_id, t1_cs, "PiH Candidate Selection", "candidate_selection",
									 "Extra Pipeline")

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
					"label": "N/A",  # default value; will be updated by PV service
					"gps_data": gps_data
				}
				L.log(LOG_NOTICE, "[PCS_RESULT] detected PiH object(s) in frame-{}".format(frame_id))
			else:
				L.log(LOG_NOTICE, "[PCS_RESULT] Unable to detect any PiH objects in frame-{}".format(frame_id))

		return mbbox_data, plot_info

	async def start(self):
		channel = "node-" + self.node_id
		L.log(LOG_NOTICE, "[{}][{}] YOLOv3Handler try to subsscribe to channel `{}` from [Scheduler Service]".format(
			get_current_time(), self.node_alias, channel))

		redis_key = self.node_id + "_status"

		consumer = self.rc.pubsub()
		consumer.subscribe([channel])
		for item in consumer.listen():
			if isinstance(item["data"], int):
				L.log(LOG_NOTICE, "[{}][{}] YOLOv3Handler start listening to [Scheduler Service]".format(
					get_current_time(), self.node_alias))
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
					"frame_id": 1,
				}
				"""
				image_info = pubsub_to_json(item["data"])
				L.log(LOG_NOTICE, "Collecting Image Info")
				L.log(LOG_NOTICE, json.dumps(image_info))
				L.log(LOG_NOTICE, "Image INFORMATION is collected.")

				if redis_get(self.rc, channel) is not None:
					self.rc.delete(channel)
					L.log(LOG_NOTICE, "[{}][{}] Forced to exit the Object Detection Service".format(
						get_current_time(), self.node_alias))
					await self.stop()
					break

				L.log(LOG_NOTICE, "Try to collect Image DATA.")
				is_success, frame_id, t0_zmq, raw_img = await self.DetectionAlgorithmService.get_img()
				L.log(LOG_NOTICE, "Receiving image data via ZMQ (is_success=%s; frame_id=%s)" % (str(is_success), str(frame_id)))
				L.log(LOG_NOTICE, "Image DATA is collected.")
				t1_zmq = (time.time() - t0_zmq) * 1000  # TODO: This is still INVALID! it got mixed up with Det latency!
				L.log(LOG_NOTICE, '[{}] Latency for Receiving Image ZMQ (%.3f ms)'.format(get_current_time()) % t1_zmq)
				# TODO: To save latency into ElasticSearchDB (Future work)

				# try to decompress the captured image (depends on the config)
				t0_decompress_in_subprocess = time.time()
				if self.compressed_img:
					# captured image is compressed, try to decompress
					t0_decompress_in_subprocess = time.time()
					deimg_len = list(raw_img.shape)[0]
					decoded_img = raw_img.reshape(deimg_len, 1)
					decompressed_img = cv2.imdecode(decoded_img, 1)  # decompress
					img = decompressed_img.copy()
				else:
					img = raw_img.copy()
				t1_decompress_in_subprocess = (time.time() - t0_decompress_in_subprocess) * 1000
				L.log(LOG_NOTICE, '[{}] Proc. Latency of %s for frame-%s (%.3f ms)'.format(get_current_time()) % (
						"DECOMPRESS-IN-DETECTION-SERVICE", str(image_info["frame_id"]), t1_decompress_in_subprocess))

				# ensure that the input image has a FullHD image resolution
				img, img_resizer_lat = await self.ResizerService.ensure_fullhd_image_input(img)

				# BUG FIX: Start t0 e2e frame from here (later on, PLUS with `t1_zmq` latency)
				t0_e2e_latency = time.time()

				# flag to set whether the PiH detection can capture any PiH object or not!
				detection_status = False

				# Start performing object detection
				L.log(LOG_NOTICE, "Start performing object detection")
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
														 image4yolo_lat, pred_lat, frame_id, image_info, img_resizer_lat)
					# execute PiH Candidate Selection & PiH Persitance Validation
					mbbox_data, plot_info = await self._exec_extra_pipeline(img, bbox_data, mbbox_data, plot_info,
																			det, names, frame_id, image_info["drone_id"])

					if len(mbbox_data) > 0:
						detection_status = True
					else:
						# TODO: inform Visualizer Service ASAB!
						pass

				# Else, No object detected!
				else:
					L.log(LOG_NOTICE, "[DETECTION_RESULT] Unable to detect any valid objects in frame-{}".format(frame_id))
					# TODO: inform Visualizer Service ASAB!

				# If enable visualizer, send the bbox into the Visualizer Service
				# mode 1: `sorter`
				# mode 2: `direct`
				if self.cv_out and self.viz_com_mode == self.VizCommunicationMode.SORTER.value:
					# Send processed frame info into sorter
					# build channel
					sorter_channel = "{}_{}".format(
						self.ch_prefix,
						str(image_info["drone_id"]),
					)
					L.log(LOG_NOTICE, "[SENDING_TO_SORTER] Sending frame-{} (Drone-{}) to Sorter `{}`".format(
						frame_id, image_info["drone_id"], sorter_channel
					))
					# build frame sequence information
					frame_seq_obj = {
						"drone_id": int(image_info["drone_id"]),
						"frame_id": int(frame_id),
						"mbbox_data": mbbox_data,
						"plot_info": plot_info,
						"node_alias": self.node_alias,
					}
					pub(self.rc, sorter_channel, json.dumps(frame_seq_obj))

					# IMPORTANT: it will send the detection result (plot_info) once sorted

				elif self.cv_out and self.viz_com_mode == self.VizCommunicationMode.DIRECT.value:
					L.error(" ## MODE @ (DIRECT) IS DISABLED AT THE MOMENT!")
					# # Inform visualizer!
					# t0_plotinfo_saving = time.time()
					# drone_id = asab.Config["stream:config"]["drone_id"]
					# plot_info_key = "plotinfo-drone-%s-frame-%s" % (drone_id, str(frame_id))
					# redis_set(self.rc, plot_info_key, plot_info, expired=10)  # delete value after 10 seconds
					# t1_plotinfo_saving = (time.time() - t0_plotinfo_saving) * 1000
					# L.log(LOG_NOTICE, '[%s] Latency of Storing Plot info in redisDB (%.3f ms)' %
					# 		  (get_current_time(), t1_plotinfo_saving))

				# when no BBox not PiH detected, directly inform Visualizer service!
				if self.cv_out and not detection_status:
					# build plot_info
					# collect latest GPS Data
					gps_data = await self.GPSCollectorService.get_gps_data()

					plot_info = {
						"bbox": [],
						"mbbox": [],
						"color": "",
						"label": "Pih not found",
						"gps_data": gps_data
					}

					# Inform visualizer!
					t0_plotinfo_saving = time.time()
					drone_id = asab.Config["stream:config"]["drone_id"]
					plot_info_key = "plotinfo-drone-%s-frame-%s" % (drone_id, str(frame_id))
					redis_set(self.rc, plot_info_key, plot_info, expired=10)  # delete value after 10 seconds
					t1_plotinfo_saving = (time.time() - t0_plotinfo_saving) * 1000
					L.log(LOG_NOTICE, '[%s] Latency of Storing Plot info in redisDB (%.3f ms)' %
							  (get_current_time(), t1_plotinfo_saving))

				L.log(LOG_NOTICE, "[%s][%s][%s] Store BBox INTO Visualizer Service!" %
						  (get_current_time(), self.node_alias, str(frame_id)))

				# Set this node as available again
				redis_set(self.rc, redis_key, True)
				L.log(LOG_NOTICE, "[DOD_DEBUG] Status of this Node: %s" % str(redis_get(self.rc, redis_key)))

				# Capture and store e2e latency
				t1_e2e_latency = (time.time() - t0_e2e_latency) * 1000
				t1_e2e_latency = t1_e2e_latency + t1_zmq
				# if t_start is None:
				#     t_start = time.time()
				# else:
				#     t1_e2e_latency = t1_e2e_latency - t_start
				#     t_start = t1_e2e_latency
				await self._store_e2e_latency(str(frame_id), t1_e2e_latency)

			L.log(LOG_NOTICE, "[%s] Node-%s is ready to serve." % (get_current_time(), self.node_name))

		L.log(LOG_NOTICE, "[%s][%s] YOLOv3Handler stopped listening to [Scheduler Service]" %
			  (get_current_time(), self.node_alias))
		# Call stop function since it no longers listening
		await self.stop()

	async def _store_e2e_latency(self, frame_id, t1_e2e_latency):
		L.log(LOG_NOTICE, '[%s] E2E Latency of frame-%s (%.3f ms)' % (get_current_time(), frame_id, t1_e2e_latency))
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
		L.log(LOG_NOTICE, '\n[%s] Latency for waiting redis key e2e latency (%.3f ms)' % (get_current_time(), t1_e2e_waiting))

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
		if not await self.lat_collector_svc.store_latency_data_thread(preproc_latency_data):
			await self.stop()
		t1_preproc = (time.time() - t0_preproc) * 1000
		L.log(LOG_NOTICE, '[%s] Proc. Latency of %s (%.3f ms)' % (get_current_time(), section, t1_preproc))
