import asab
from asab import LOG_NOTICE
import logging
import time
from ext_lib.utils import get_current_time
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import pub, redis_get, redis_set
from zenoh_image_subscriber.service import ZenohImageSubscriberService
from zenoh_lib.functions import extract_compressed_tagged_img, scale_image
import simplejson as json

###

L = logging.getLogger(__name__)


###


class ImgConsumerService(ZenohImageSubscriberService):
	""" A class to extract images"""
	def __init__(self, app, service_name="offloader.ImgConsumerService"):
		super().__init__(app, service_name)

		# services
		self.ResizerService = app.get_service("scheduler.ResizerService")
		self.ZMQService = app.get_service("eagleeye.ZMQService")
		self.SchPolicyService = app.get_service("offloader.SchedulingPolicyService")

		# start pub/sub
		self.redis = MyRedis(asab.Config)

		# params for extractor
		self.cap = None
		self.frame_id = 0
		# Special params: from YOLO's config items
		self.img_size = asab.Config["objdet:yolo"].getint("img_size")
		self.half = asab.Config["objdet:yolo"].getboolean("half")
		# self._is_auto_restart = bool(int(asab.Config["stream:config"]["auto_restart"]))
		# self._restart_delay = float(asab.Config["stream:config"]["restart_delay"])
		# self._num_skipped_frames = int(asab.Config["stream:config"]["num_skipped_frames"])

		# self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

		self.LatCollectorService = app.get_service("eagleeye.LatencyCollectorService")

		self._is_running = True  # TODO: we need to dynamically adjust the value

		# input and source image resolution
		self.img_w = asab.Config["stream:config"].getint("width")
		self.img_h = asab.Config["stream:config"].getint("height")
		self.img_ch = asab.Config["stream:config"].getint("channel")

		self._num_skipped_frames = asab.Config["stream:config"].getint("num_skipped_frames")

		self.decompression = asab.Config["image:preprocessing"].getboolean("decompression")

		# config related with ZENOH; default value
		self.received_frame_id = 0
		self.skip_count = -1
		# self.comsumer_type = asab.Config["zenoh"].getint("comsumer_type")

		# Scheduling policy
		self.scheduler_policy = asab.Config["scheduler_policy"]["policy"]

		self.to_fullhd = asab.Config["image:preprocessing"].getboolean("to_fullhd")

	# in this case, it has collected the latest available nodes
	async def start_zenoh_consumer(self, config):
		L.log(LOG_NOTICE, "#### I am extractor ZENOH function!")

		# set config
		self.ZMQService.set_config(config)
		await self.override_zenoh_config(config)

		# get list of available nodes
		avail_nodes = self.ZMQService.get_available_nodes()

		# apply nodes as the workers
		await self.SchPolicyService.initialize_available_nodes(avail_nodes)

		# Reset frame_id and other related variables
		self.frame_id = 0
		self.received_frame_id = 0
		self.skip_count = -1

		await self.start_zenoh_subscription()

	def _sync_save_latency(self, frame_id, latency, algorithm="[?]", section="[?]", cat="Object Detection",
							node_id="-", node_name="-"):
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
		if not self.LatCollectorService.sync_store_latency_data_thread(preproc_latency_data):
			L.error("[{}]Ups, it failed to save the latency data (Scheduling latency)".format(get_current_time()))

	def _exec_e2e_latency_collector(self, t0_e2e_lat, node_id, frame_id):
		t0_thread = time.time()
		try:
			kwargs = {
				# TODO: To add DroneID as the key as well (Future work)
				"lat_key": node_id + "-%s" % str(frame_id) + "-e2e-latency",
				"t0": t0_e2e_lat
			}
			self.executor.submit(self._save_e2e_lat, **kwargs)
		except Exception as e:
			L.error("[%s][{}] Somehow we unable to Start the Thread of "
					"e2e Latency Collector: `{}`".format(frame_id, str(e)) % get_current_time())

		t1_thread = (time.time() - t0_thread) * 1000
		L.log(LOG_NOTICE, '[{}] Latency for Start threading (%.3f ms)'.format(get_current_time()) % t1_thread)
		# TODO: Save the latency into ElasticSearchDB for the real-time monitoring

	def _save_e2e_lat(self, lat_key, t0):
		redis_set(self.redis.get_rc(), lat_key, t0, expired=30)  # set expired in 30 second

	def save_all_captured_latency_data(self, frame_id, latency_data):
		for cat, lat in latency_data.items():
			# Save Scheduling latency
			self._sync_save_latency(
				frame_id, lat, "", "preproc", cat, "", ""
			)
			# L.warning('[%s] Proc. Latency of %s for frame-%s (%.3f ms)' % (
			# 	get_current_time(), "preproc-{}".format(cat), str(frame_id), lat))

	def ensure_fullhd_image_input(self, img):
		# perform the image size conversion ONLY when the image is decompressed (decompression=False)
		new_img = img.copy()
		if self.decompression:
			print(" >>> img:", type(img))
			print(" >>> new_img:", type(new_img))
			img_height, img_weight, _ = new_img.shape

			if img_height != self.img_h:
				new_img = scale_image(new_img, self.img_h, self.img_w)

		return new_img

	# OVERRIDE Child function
	def img_listener(self, consumed_data):
		img_info, latency_data = extract_compressed_tagged_img(consumed_data, is_decompress=self.decompression)
		"""
		latency_data = {
			"decoding_payload": t1_decode,
			"clean_decoded_payload": t1_non_img_cleaning,
			"extract_img_data": t1_img_extraction,
			"decompress_img": t1_decompress_img,
			"zenoh_pubsub": zenoh_pubsub_latency,
			"compress_img": img_compr_lat,
		}
	
		# decode data
		img_info = {
			"id": drone_id,
			"img": decompressed_img,
			"timestamp": t0_zenoh_pubsub,
			"frame_id": frame_id,
		}
		"""

		# try to scale up/down into fullhd (if enabled)
		if self.to_fullhd:
			img_info["img"] = self.ensure_fullhd_image_input(img_info["img"])

		self.save_all_captured_latency_data(img_info["frame_id"], latency_data)

		# ########## Processing comsumed frame data
		# print(" ## # ########## Processing comsumed frame data")

		_senders = self.ZMQService.get_senders()
		_config = self.ZMQService.get_config()

		###################################
		# Start the pipeline to use the captured image data
		self.received_frame_id += 1
		self.skip_count += 1

		# success, t0_zenoh_source, frame = True, img_info["timestamp"], img_info["img"]
		success, t0_zenoh_source, frame = True, img_info["timestamp"], img_info["img"]

		# try skipping frames
		if self._num_skipped_frames > 0 and self.received_frame_id > 1 and self.skip_count <= self._num_skipped_frames:
			# skip this frame
			L.log(LOG_NOTICE, ">>> Skipping frame-{}; Current `skip_count={}`".format(str(self.received_frame_id),
																					  str(self.skip_count)))
		else:
			# self.frame_id += 1
			self.frame_id = int(img_info["frame_id"])

			# Sending image data into Visualizer Service as well
			# self.ZMQService.send_image_to_visualizer(self.frame_id, frame)
			self.ZMQService.send_image_to_visualizer_v2(img_info["id"], self.frame_id, frame)

			# Start t0_e2e_lat: To calculate the e2e processing & comm. latency
			t0_e2e_lat = time.time()

			# Perform scheduling based on Round-Robin fashion (Default)
			t0_sched_lat = time.time()
			try:
				if bool(int(asab.Config["stream:config"]["test_mode"])):
					sel_node_id = 0
				else:
					sel_node_id = self.SchPolicyService.find_idle_node(
						max_node=len(_senders["node"]),
						sch_policy=self.scheduler_policy,
						frame_id=self.frame_id,
					)
				L.log(LOG_NOTICE, "Selected Node idx: {}".format(str(sel_node_id)))
			except Exception as e:
				L.error("[ERROR]: %s" % str(e))
				sel_node_id = 0
			t1_sched_lat = (time.time() - t0_sched_lat) * 1000

			# First, notify the Object Detection Service to get ready (publish)
			node_id = _senders["node"][sel_node_id]["id"]
			node_channel = _senders["node"][sel_node_id]["channel"]
			node_name = _senders["node"][sel_node_id]["name"]

			L.log(LOG_NOTICE, "NodeID={}; NodeChannel={}; NodeName={}".format(str(node_id), node_channel, node_name))

			# Save Scheduling latency
			self._sync_save_latency(
				self.frame_id, t1_sched_lat, self.scheduler_policy, "scheduling", "Scheduling", node_id, node_name
			)
			L.log(LOG_NOTICE, '[{}] Proc. Latency of %s for frame-%s (%.3f ms)'.format(get_current_time()) % (
				"scheduling", str(self.frame_id), t1_sched_lat))

			# Save e2e latency
			self._exec_e2e_latency_collector(t0_e2e_lat, node_id, self.frame_id)

			t0_other_process = time.time()
			# send data into Scheduler service through the pub/sub
			# Never send any frame if `test_mode` is enabled (test_mode=1)
			if not bool(int(asab.Config["stream:config"]["test_mode"])):
				t0_publish = time.time()
				L.log(LOG_NOTICE, "[{}] Publishing image into Redis channel: %s".format(get_current_time()) % node_channel)

				dump_request = json.dumps({
					"active": True,
					"algorithm": _config["algorithm"],
					"ts": time.time(),
					"drone_id": int(img_info["id"]),
					"frame_id": int(img_info["frame_id"]),
				})

				pub(self.redis.get_rc(), node_channel, dump_request)
				t1_publish = (time.time() - t0_publish) * 1000
				# TODO: Saving latency for scheduler:producer:notification:image
				L.log(LOG_NOTICE, '[{}] Latency for Publishing FRAME NOTIFICATION '
								  'into Object Detection Service (%.3f ms)'.format(get_current_time()) % t1_publish)

				if not bool(int(asab.Config["stream:config"]["convert_img"])):
					# Sending image data through ZMQ (TCP connection)
					L.log(LOG_NOTICE, "# Sending image data through ZMQ (TCP connection)")
					self.ZMQService.send_this_image(_senders["zmq"][sel_node_id], self.frame_id, frame)
				else:
					# TODO: In this case, Candidate Selection Algorithm will not work!!!!!
					L.log(LOG_NOTICE, "# Convert the yolo input images; "
									  "Here it converts from FullHD into <img_size> (padded size)")
					# Convert the yolo input images; Here it converts from FullHD into <img_size> (padded size)
					if not bool(int(asab.Config["stream:config"]["gpu_converter"])):
						yolo_frame = self.ResizerService.sync_cpu_convert_to_padded_size(frame)
					else:
						# NOT IMPLEMENTED YET!!!! USe CPU instead!
						yolo_frame = self.ResizerService.sync_cpu_convert_to_padded_size(frame)
						# TODO: To add GPU-based downsample function

					# CHECKING: how is the latency if we send converted version?
					# Sending image data through ZENOH (TCP connection)
					self.ZMQService.send_this_image(_senders["zmq"][sel_node_id], self.frame_id, yolo_frame)
			t1_other_process = (time.time() - t0_other_process) * 1000
			L.log(LOG_NOTICE, '[{}] Proc. Latency of %s for frame-%s (%.3f ms)'.format(get_current_time()) % (
				"OTHER PROCESSES", str(self.frame_id), t1_other_process))

		# reset skipping frames
		if 0 < self._num_skipped_frames < self.skip_count:
			self.skip_count = 0
