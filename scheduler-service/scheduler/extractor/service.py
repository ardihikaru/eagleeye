import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time
from ext_lib.redis.translator import pub
from imutils.video import FileVideoStream
from ext_lib.image_loader.load_images import LoadImages
import cv2
import time
import simplejson as json

###

L = logging.getLogger(__name__)


###


class ExtractorService(asab.Service):
	"""
		A class to extract either: Video stream or tuple of images
	"""

	def __init__(self, app, service_name="scheduler.ExtractorService"):
		super().__init__(app, service_name)
		self.ResizerService = app.get_service("scheduler.ResizerService")

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

	async def extract_folder(self, config, senders):
		print("#### I am extractor FOLDER function from ExtractorService!")
		print(config)
		dataset = await self._read_from_folder(config)

		# Loop each frame
		print()
		for i in range(len(dataset)):
			self.frame_id += 1
			path, img, im0s, vid_cap = dataset[i][0], dataset[i][1], dataset[i][2], dataset[i][3]

			try:
				success, frame = True, im0s
				print("--- success:", self.frame_id, success, frame.shape)
				# if self._detection_handler(ret, frame, received_frame_id):
				#     break

			except Exception as e:
				print(" ---- e:", e)
				break

		print("\n[%s] No more frame to show." % get_current_time())

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

	async def extract_video_stream(self, config, senders):
		print("#### I am extractor VIDEO STREAM function from ExtractorService!")
		print(config)
		try:
			# Reset frame_id
			self.frame_id = 0

			self.cap = await self._set_cap(config)

			while await self._streaming():
				self.frame_id += 1
				success, frame = await self._read_frame()
				print("\n --- success:", self.frame_id, success, frame.shape)

				# TODO: To implement scheduler here and find which node will be selected
				# Dummy and always select Node=1 now; id=0
				sel_node_id = 0

				# First, notify the Object Detection Service to get ready (publish)
				node_id = senders["node"][sel_node_id]["id"]
				node_channel = senders["node"][sel_node_id]["channel"]
				print(" >>>> node_id=", node_id)
				print(" >>>> node_channel=", node_channel)
				# send data into Scheduler service through the pub/sub
				t0_publish = time.time()
				print("# send data into Scheduler service through the pub/sub")
				dump_request = json.dumps({"active": True, "frame": "ini frame data coy"})
				pub(self.redis.get_rc(), node_channel, dump_request)
				t1_publish = (time.time() - t0_publish) * 1000
				# TODO: Saving latency for scheduler:producer:notification:image
				print('[%s] Latency for Publishing FRAME NOTIFICATION into Object Detection Service (%.3f ms)' % (
				get_current_time(), t1_publish))

				# Sending image data through ZMQ (TCP connection)
				t0_zmq = time.time()
				zmq_id = str(self.frame_id) + "-" + str(t0_zmq)
				# self.sender.send_image(str(self.frame_id), frame)
				senders["zmq"][sel_node_id].send_image(zmq_id, frame)
				t1_zmq = (time.time() - t0_zmq) * 1000
				print('Latency [Send imagezmq] of frame-%s: (%.5fms)' % (str(self.frame_id), t1_zmq))

				# Convert the yolo input images; Here it converts from FullHD into <img_size> (padded size)
				# TODO: To add GPU-based downsample function
				yolo_frame = await self.ResizerService.cpu_convert_to_padded_size(frame)
				# yolo_frame = await self.ResizerService.gpu_convert_to_padded_size(frame)
				print("--- success:", self.frame_id, success, yolo_frame.shape)

				# # CHECKING: how is the latency if we send converted version?
				# # Sending image data through ZMQ (TCP connection)
				# t0_zmq = time.time()
				# zmq_id = str(self.frame_id) + "-" + str(t0_zmq)
				# # self.sender.send_image(str(self.frame_id), frame)
				# senders["zmq"][sel_node_id].send_image(zmq_id, yolo_frame)
				# t1_zmq = (time.time() - t0_zmq) * 1000
				# print('Latency [Send imagezmq YOLO Img] of frame-%s: (%.5fms)' % (str(self.frame_id), t1_zmq))

				print()

		except Exception as e:
			# print(" ---- >> e:", e)
			return False
			# TODO: To have further actions, i.e. restart connection (work for both Video file / Streaming
			# TODO: When reloaded, we need to clean up: RedisDB and any other storage related to this action

	async def _set_cap(self, config):
		if bool(asab.Config["stream:config"]["thread"]):
			return FileVideoStream(config["uri"]).start()  # Thread-based video capture
		else:
			return cv2.VideoCapture(config["uri"])

	async def _streaming(self):
		if bool(asab.Config["stream:config"]["thread"]):
			return self.cap.more()
		else:
			return True

	async def _read_frame(self):
		if bool(asab.Config["stream:config"]["thread"]):
			return True, self.cap.read()
		else:
			return self.cap.read()
