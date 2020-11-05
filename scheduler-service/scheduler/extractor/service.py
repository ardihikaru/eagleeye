import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time
from ext_lib.redis.translator import pub, redis_set, redis_get
from imutils.video import FileVideoStream
from ext_lib.image_loader.load_images import LoadImages
import cv2
import time
import simplejson as json
from concurrent.futures import ThreadPoolExecutor
from ext_lib.utils import get_imagezmq

###

L = logging.getLogger(__name__)


###


class ExtractorService(asab.Service):
	""" A class to extract either: Video stream or tuple of images """

	def __init__(self, app, service_name="scheduler.ExtractorService"):
		super().__init__(app, service_name)
		self.ResizerService = app.get_service("scheduler.ResizerService")
		self.ZMQService = app.get_service("scheduler.ZMQService")
		self.SchPolicyService = app.get_service("scheduler.SchedulingPolicyService")
		self.TCPCameraServerService = app.get_service("scheduler.TCPCameraServerService")

		# start pub/sub
		self.redis = MyRedis(asab.Config)

		# params for extractor
		self.cap = None
		self.frame_id = 0
		# Special params: from YOLO's config items
		self.img_size = int(asab.Config["objdet:yolo"]["img_size"])
		self.half = bool(asab.Config["objdet:yolo"]["half"])
		self.source_folder_prefix = asab.Config["objdet:yolo"]["source_folder_prefix"]
		self.file_ext = asab.Config["objdet:yolo"]["file_ext"]

		self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

		self.LatCollectorService = app.get_service("scheduler.LatencyCollectorService")

	# async def extract_folder(self, config, senders):
	# TODO: This function is currently not being tested YET
	async def extract_folder(self, config):
		L.warning("#### I am extractor FOLDER function from ExtractorService!")
		senders = self.ZMQService.get_senders()

		dataset = await self._read_from_folder(config)

		# Loop each frame
		for i in range(len(dataset)):
			self.frame_id += 1
			path, img, im0s, vid_cap = dataset[i][0], dataset[i][1], dataset[i][2], dataset[i][3]

			try:
				success, frame = True, im0s
				# print("--- success:", self.frame_id, success, frame.shape)
				# if self._detection_handler(ret, frame, received_frame_id):
				#     break

			except Exception as e:
				L.error("[ERROR]: %s" % str(e))
				break

		L.warning("\n[%s] No more frame to show." % get_current_time())

	async def _read_from_folder(self, config):
		"""
			Capture images from the source path folder, then, store them in the local variable
		"""
		# Set Dataloader
		unordered_dataset = LoadImages(config["uri"], img_size=self.img_size, half=self.half)
		# order image index
		return await self._get_ordered_img(config, unordered_dataset)

	async def _get_ordered_img(self, config, dataset):
		"""
			Get ordered images
		"""
		max_img = len(dataset)
		ordered_dataset = []
		for i in range(max_img):
			ordered_dataset.append([])

		i = 0
		for path, img, im0s, vid_cap in dataset:
			prefix = self.source_folder_prefix
			# removed_str = self.opt.source + prefix
			removed_str = config["uri"] + prefix
			real_frame_idx = int((path.replace(removed_str, "")).replace(self.file_ext, ""))
			real_idx = real_frame_idx - 1
			ordered_dataset[real_idx] = [path, img, im0s, vid_cap]
			i += 1

		return ordered_dataset

	def _save_e2e_lat(self, lat_key, t0):
		redis_set(self.redis.get_rc(), lat_key, t0, expired=30)  # set expired in 30 second

	def _exec_e2e_latency_collector(self, t0_e2e_lat, node_id, frame_id):
		t0_thread = time.time()
		try:
			kwargs = {
				# TODO: To add DroneID as the key as well (Future work)
				"lat_key": node_id + "-%s" % str(frame_id) + "-e2e-latency",
				"t0": t0_e2e_lat
			}
			self.executor.submit(self._save_e2e_lat, **kwargs)
		except:
			L.warning("\n[%s] Somehow we unable to Start the Thread of e2e Latency Collector" % get_current_time())
		t1_thread = (time.time() - t0_thread) * 1000
		L.warning('\n[%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_thread))
		# TODO: Save the latency into ElasticSearchDB for the real-time monitoring

	async def _save_latency(self, frame_id, latency, algorithm="[?]", section="[?]", cat="Object Detection",
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
		if not await self.LatCollectorService.store_latency_data_thread(preproc_latency_data):
			L.warning("[%s]\nUps, it failed to save the latency data (Scheduling latency)" % get_current_time())

	# async def extract_video_stream(self, config, senders):
	async def extract_video_stream(self, config):
		L.warning("#### I am extractor VIDEO STREAM function from ExtractorService!")
		senders = self.ZMQService.get_senders()

		try:
			# Reset frame_id
			self.frame_id = 0

			self.cap = await self._set_cap(config)

			while await self._streaming():
				self.frame_id += 1
				success, frame = await self._read_frame()

				# Sending image data into Visualizer Service as well
				self.ZMQService.send_image_to_visualizer(self.frame_id, frame)

				# Start t0_e2e_lat: To calculate the e2e processing & comm. latency
				t0_e2e_lat = time.time()

				# Perform scheduling based on Round-Robin fasion (Default)
				t0_sched_lat = time.time()
				try:
					if bool(int(asab.Config["stream:config"]["test_mode"])):
						sel_node_id = 0
					else:
						sel_node_id = await self.SchPolicyService.schedule(max_node=len(senders["node"]))
					L.warning("Selected Node idx: %s" % str(sel_node_id))
				except Exception as e:
					L.error("[ERROR]: %s" % str(e))
				t1_sched_lat = (time.time() - t0_sched_lat) * 1000
				# TODO: To implement scheduler here and find which node will be selected

				# First, notify the Object Detection Service to get ready (publish)
				node_id = senders["node"][sel_node_id]["id"]
				node_channel = senders["node"][sel_node_id]["channel"]
				node_name = senders["node"][sel_node_id]["name"]

				L.warning("NodeID=%s; NodeChannel=%s; NodeName=%s" % (str(node_id), node_channel, node_name))

				# Save Scheduling latency
				await self._save_latency(
					self.frame_id, t1_sched_lat, "Round-Robin", "scheduling", "Scheduling", node_id, node_name
				)
				L.warning('\n[%s] Proc. Latency of %s for frame-%s (%.3f ms)' % (
					get_current_time(), "scheduling", str(self.frame_id), t1_sched_lat))

				# Save e2e latency
				self._exec_e2e_latency_collector(t0_e2e_lat, node_id, self.frame_id)

				# send data into Scheduler service through the pub/sub
				# Never send any frame if `test_mode` is enabled (test_mode=1)
				if not bool(int(asab.Config["stream:config"]["test_mode"])):
					t0_publish = time.time()
					L.warning("[%s] Publishing image into Redis channel: %s" % (get_current_time(), node_channel))
					dump_request = json.dumps({"active": True, "algorithm": config["algorithm"], "ts": time.time()})
					pub(self.redis.get_rc(), node_channel, dump_request)
					t1_publish = (time.time() - t0_publish) * 1000
					# TODO: Saving latency for scheduler:producer:notification:image
					L.warning(
						'[%s] Latency for Publishing FRAME NOTIFICATION into Object Detection Service (%.3f ms)' % (
							get_current_time(), t1_publish)
						)

					if not bool(int(asab.Config["stream:config"]["convert_img"])):
						# Sending image data through ZMQ (TCP connection)
						self.ZMQService.send_this_image(senders["zmq"][sel_node_id], self.frame_id, frame)
					else:
						# TODO: In this case, Candidate Selection Algorithm will not work!!!!!
						# Convert the yolo input images; Here it converts from FullHD into <img_size> (padded size)
						if not bool(int(asab.Config["stream:config"]["gpu_converter"])):
							yolo_frame = await self.ResizerService.cpu_convert_to_padded_size(frame)
						else:
							# NOT IMPLEMENTED YET!!!!
							# TODO: To add GPU-based downsample function
							yolo_frame = await self.ResizerService.gpu_convert_to_padded_size(frame)

						# CHECKING: how is the latency if we send converted version?
						# Sending image data through ZMQ (TCP connection)
						self.ZMQService.send_this_image(senders["zmq"][sel_node_id], self.frame_id, yolo_frame)

		except Exception as e:
			L.error("[ERROR] extractor/service.py > def extract_video_stream(): %s" % str(e))
			return False
			# TODO: To have further actions, i.e. restart connection (work for both Video file / Streaming
			# TODO: When reloaded, we need to clean up: RedisDB and any other storage related to this action

	async def extract_image_zmq(self, config):
		L.warning("#### I am extractor IMAGE ZMQ function from ExtractorService!")
		senders = self.ZMQService.get_senders()

		# extract `uri` to collect `host` and `port`
		uri_detail = config["uri"].split(":")

		# Set ZMQ Source Reader
		await self.ZMQService.initialize_zmq_source_reader(
			zmq_source_host=uri_detail[0],
			zmq_source_port=uri_detail[1]
		)
		zmq_source_reader = self.ZMQService.get_zmq_source_reader()

		try:
			while True:
				success, frame_id, t0_zmq_soure, frame = get_imagezmq(zmq_source_reader)
				t1_zmq_soure = (time.time() - t0_zmq_soure) * 1000
				self.frame_id = int(frame_id)

				# Save latency of receiving image from souce
				await self._save_latency(
					self.frame_id, t1_zmq_soure, "-", "imagezmq", "reading_source"
				)
				L.warning('\n[%s] Communication Latency of %s for frame-%s (%.3f ms)' % (
					get_current_time(), "[Receiving Image with IMAGEZMQ]", str(self.frame_id), t1_zmq_soure))

				# Sending image data into Visualizer Service as well
				self.ZMQService.send_image_to_visualizer(self.frame_id, frame)

				# Start t0_e2e_lat: To calculate the e2e processing & comm. latency
				t0_e2e_lat = time.time()

				# Perform scheduling based on Round-Robin fasion (Default)
				t0_sched_lat = time.time()
				try:
					if bool(int(asab.Config["stream:config"]["test_mode"])):
						sel_node_id = 0
					else:
						sel_node_id = await self.SchPolicyService.schedule(max_node=len(senders["node"]))
					L.warning("Selected Node idx: %s" % str(sel_node_id))
				except Exception as e:
					L.error("[ERROR]: %s" % str(e))
				t1_sched_lat = (time.time() - t0_sched_lat) * 1000
				# TODO: To implement scheduler here and find which node will be selected

				# First, notify the Object Detection Service to get ready (publish)
				node_id = senders["node"][sel_node_id]["id"]
				node_channel = senders["node"][sel_node_id]["channel"]
				node_name = senders["node"][sel_node_id]["name"]

				L.warning("NodeID=%s; NodeChannel=%s; NodeName=%s" % (str(node_id), node_channel, node_name))

				# Save Scheduling latency
				await self._save_latency(
					self.frame_id, t1_sched_lat, "Round-Robin", "scheduling", "Scheduling", node_id, node_name
				)
				L.warning('\n[%s] Proc. Latency of %s for frame-%s (%.3f ms)' % (
					get_current_time(), "scheduling", str(self.frame_id), t1_sched_lat))

				# Save e2e latency
				self._exec_e2e_latency_collector(t0_e2e_lat, node_id, self.frame_id)

				# send data into Scheduler service through the pub/sub
				# Never send any frame if `test_mode` is enabled (test_mode=1)
				if not bool(int(asab.Config["stream:config"]["test_mode"])):
					t0_publish = time.time()
					L.warning("[%s] Publishing image into Redis channel: %s" % (get_current_time(), node_channel))
					dump_request = json.dumps({"active": True, "algorithm": config["algorithm"], "ts": time.time()})
					pub(self.redis.get_rc(), node_channel, dump_request)
					t1_publish = (time.time() - t0_publish) * 1000
					# TODO: Saving latency for scheduler:producer:notification:image
					L.warning(
						'[%s] Latency for Publishing FRAME NOTIFICATION into Object Detection Service (%.3f ms)' % (
							get_current_time(), t1_publish)
						)

					if not bool(int(asab.Config["stream:config"]["convert_img"])):
						# Sending image data through ZMQ (TCP connection)
						self.ZMQService.send_this_image(senders["zmq"][sel_node_id], self.frame_id, frame)
					else:
						# TODO: In this case, Candidate Selection Algorithm will not work!!!!!
						# Convert the yolo input images; Here it converts from FullHD into <img_size> (padded size)
						if not bool(int(asab.Config["stream:config"]["gpu_converter"])):
							yolo_frame = await self.ResizerService.cpu_convert_to_padded_size(frame)
						else:
							# NOT IMPLEMENTED YET!!!!
							# TODO: To add GPU-based downsample function
							yolo_frame = await self.ResizerService.gpu_convert_to_padded_size(frame)

						# CHECKING: how is the latency if we send converted version?
						# Sending image data through ZMQ (TCP connection)
						self.ZMQService.send_this_image(senders["zmq"][sel_node_id], self.frame_id, yolo_frame)

		except Exception as e:
			L.error("[ERROR] extractor/service.py > def extract_image_zmq(): %s" % str(e))
			return False
			# TODO: To have further actions, i.e. restart connection (work for both Video file / Streaming
			# TODO: When reloaded, we need to clean up: RedisDB and any other storage related to this action

	async def extract_image_tcp(self, config):
		L.warning("#### I am extractor TCP function from ExtractorService!")
		senders = self.ZMQService.get_senders()

		# extract `uri` to collect `host` and `port`
		uri_detail = config["uri"].split(":")

		# Set ZMQ Source Reader
		await self.TCPCameraServerService.initialize_camera_source_reader(
			_tcp_host=uri_detail[0],
			_tcp_port=int(uri_detail[1])
		)
		tcp_conn = self.TCPCameraServerService.get_tcp_conn()

		try:
			# Reset frame_id
			self.frame_id = 0

			while True:
				self.frame_id += 1

				success, frame_id, t0_zmq_soure, frame = await self.TCPCameraServerService.get_image(self.frame_id)
				# t1_zmq_soure = (time.time() - t0_zmq_soure) * 1000

				# # Save latency of receiving image from souce
				# await self._save_latency(
				# 	self.frame_id, t1_zmq_soure, "-", "imagezmq", "reading_source"
				# )
				# L.warning('\n[%s] Communication Latency of %s for frame-%s (%.3f ms)' % (
				# 	get_current_time(), "[Receiving Image with IMAGEZMQ]", str(self.frame_id), t1_zmq_soure))

				# Sending image data into Visualizer Service as well
				self.ZMQService.send_image_to_visualizer(self.frame_id, frame)

				# Start t0_e2e_lat: To calculate the e2e processing & comm. latency
				t0_e2e_lat = time.time()

				# Perform scheduling based on Round-Robin fasion (Default)
				t0_sched_lat = time.time()
				try:
					if bool(int(asab.Config["stream:config"]["test_mode"])):
						sel_node_id = 0
					else:
						sel_node_id = await self.SchPolicyService.schedule(max_node=len(senders["node"]))
					L.warning("Selected Node idx: %s" % str(sel_node_id))
				except Exception as e:
					L.error("[ERROR]: %s" % str(e))
				t1_sched_lat = (time.time() - t0_sched_lat) * 1000
				# TODO: To implement scheduler here and find which node will be selected

				# First, notify the Object Detection Service to get ready (publish)
				node_id = senders["node"][sel_node_id]["id"]
				node_channel = senders["node"][sel_node_id]["channel"]
				node_name = senders["node"][sel_node_id]["name"]

				L.warning("NodeID=%s; NodeChannel=%s; NodeName=%s" % (str(node_id), node_channel, node_name))

				# Save Scheduling latency
				await self._save_latency(
					self.frame_id, t1_sched_lat, "Round-Robin", "scheduling", "Scheduling", node_id, node_name
				)
				L.warning('\n[%s] Proc. Latency of %s for frame-%s (%.3f ms)' % (
					get_current_time(), "scheduling", str(self.frame_id), t1_sched_lat))

				# Save e2e latency
				self._exec_e2e_latency_collector(t0_e2e_lat, node_id, self.frame_id)

				# send data into Scheduler service through the pub/sub
				# Never send any frame if `test_mode` is enabled (test_mode=1)
				if not bool(int(asab.Config["stream:config"]["test_mode"])):
					t0_publish = time.time()
					L.warning("[%s] Publishing image into Redis channel: %s" % (get_current_time(), node_channel))
					dump_request = json.dumps({"active": True, "algorithm": config["algorithm"], "ts": time.time()})
					pub(self.redis.get_rc(), node_channel, dump_request)
					t1_publish = (time.time() - t0_publish) * 1000
					# TODO: Saving latency for scheduler:producer:notification:image
					L.warning(
						'[%s] Latency for Publishing FRAME NOTIFICATION into Object Detection Service (%.3f ms)' % (
							get_current_time(), t1_publish)
						)

					if not bool(int(asab.Config["stream:config"]["convert_img"])):
						# Sending image data through ZMQ (TCP connection)
						self.ZMQService.send_this_image(senders["zmq"][sel_node_id], self.frame_id, frame)
					else:
						# TODO: In this case, Candidate Selection Algorithm will not work!!!!!
						# Convert the yolo input images; Here it converts from FullHD into <img_size> (padded size)
						if not bool(int(asab.Config["stream:config"]["gpu_converter"])):
							yolo_frame = await self.ResizerService.cpu_convert_to_padded_size(frame)
						else:
							# NOT IMPLEMENTED YET!!!!
							# TODO: To add GPU-based downsample function
							yolo_frame = await self.ResizerService.gpu_convert_to_padded_size(frame)

						# CHECKING: how is the latency if we send converted version?
						# Sending image data through ZMQ (TCP connection)
						self.ZMQService.send_this_image(senders["zmq"][sel_node_id], self.frame_id, yolo_frame)

		except Exception as e:
			L.error("[ERROR] extractor/service.py > def extract_image_tcp(): %s" % str(e))
			return False
			# TODO: To have further actions, i.e. restart connection (work for both Video file / Streaming
			# TODO: When reloaded, we need to clean up: RedisDB and any other storage related to this action

	async def _set_cap(self, config):
		if bool(int(asab.Config["stream:config"]["thread"])):
			return FileVideoStream(config["uri"]).start()  # Thread-based video capture
		else:
			return cv2.VideoCapture(config["uri"])

	async def _streaming(self):
		if bool(int(asab.Config["stream:config"]["thread"])):
			return self.cap.more()
		else:
			return self.cap.isOpened()

	async def _read_frame(self):
		if bool(int(asab.Config["stream:config"]["thread"])):
			return True, self.cap.read()
		else:
			return self.cap.read()
