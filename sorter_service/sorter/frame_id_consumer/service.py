import asab
from enum import Enum
import logging
import time
from ext_lib.utils import get_current_time, pubsub_to_json
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_set

###

L = logging.getLogger(__name__)


###


class FrameIDConsumerService(asab.Service):

	def __init__(self, app):
		super().__init__(app, "sorter.FrameIDConsumerService")

		self.lat_collector_svc = app.get_service("eagleeye.LatencyCollectorService")

		self.algorithm_svc = app.get_service("sorter.AlgorithmService")

		self.sorter_id = asab.Config["identity"].getint("id")
		self.ch_prefix = asab.Config["identity"]["ch_prefix"]
		self.channel = None

		# sorting strategy
		self.max_pool = asab.Config["strategy"].getint("max_pool")

		self.highest_seq_id = 0

		self.rc = MyRedis(asab.Config).get_rc()

	async def initialize(self, app):
		# build redis channel name
		self.channel = "{}_{}".format(
			self.ch_prefix,
			self.sorter_id,
		)

	async def start_subscription(self):
		"""
		Cansume data produced by: `detection/algorithm/handler.py`:
		```
			...
			async def start(self):
			...
				# Send processed frame info into sorter
				# build channel
				sorter_channel = "{}_{}".format(
					self.ch_prefix,
					str(image_info["drone_id"]),
				)
				# build frame sequence information
				frame_seq_obj = {
					"drone_id": int(image_info["drone_id"]),
					"frame_id": int(frame_id),
					"plot_info": plot_info,
				}
				pub(self.rc, sorter_channel, json.dumps(frame_seq_obj))
			...
		```
		"""
		consumer = self.rc.pubsub()
		consumer.subscribe([self.channel])

		data_pool = {}  # list of detection result
		unsorted_seq = []  # list of frame_id based on captured data through redis consumer
		for item in consumer.listen():
			if isinstance(item["data"], int):
				L.warning("[{}] Starting subscription to channel `{}_{}`".format(
						  get_current_time(), self.ch_prefix, self.sorter_id
				))
			else:
				detection_result = pubsub_to_json(item["data"])
				"""
				Sample Data: {'drone_id': 2, 'frame_id': 9207, 'plot_info': {}
				"""
				L.warning("[CONSUMED_DATA] {}".format(detection_result))

				# pull in captured data
				data_pool[detection_result["frame_id"]] = detection_result

				unsorted_seq.append(detection_result["frame_id"])

				# count total number of pulled data
				# if total pool is equal to the `max_pool`,
				# 1. send the list into sorter algorithm
				# 2. send each sorted detection result to the visualizer
				if len(unsorted_seq) > 0 and len(unsorted_seq) % self.max_pool == 0:
					await self.sort_and_wait(unsorted_seq, data_pool)

					# reset pool
					data_pool = {}
					unsorted_seq = []

	async def filter_sorted_seq(self, sorted_seq, _highest_seq_id):
		""" Drop an id which is lower than `_highest_seq_id` """
		for seq in sorted_seq:
			if seq < _highest_seq_id:
				sorted_seq.remove(seq)

		return sorted_seq

	async def sort_and_wait(self, unsorted_seq, data_pool):
		"""
		Sort a tuple of frame ids. Once sorted, send each detection result to the visualizer service.
		While performing this sorting, the Consumer is halted for a while.
		"""
		# sort frame
		t0_sorting = time.time()
		sorted_seq = await self.algorithm_svc.sort_frame_sequences(unsorted_seq)
		t1_sorting = (time.time() - t0_sorting) * 1000
		L.warning('[%s] Latency of Sorting a frame sequence (%.3f ms)' %
				  (get_current_time(), t1_sorting))

		# build & submit latency data: Sorting
		L.warning("[%s] build & submit latency data: Pre-processing" % get_current_time())
		# IMPORTANT: `frame_id` is set into None
		await self.lat_collector_svc.build_and_save_latency_info(
			None, t1_sorting, "Sorting Network", "scheduling", "sorting"
		)

		# for each frame, send the result to the visualizer
		if sorted_seq is not None:
			# drop old sequences
			sorted_seq = await self.filter_sorted_seq(sorted_seq.copy(), self.highest_seq_id)

			# update highest sequence id
			self.highest_seq_id = sorted_seq[-1]

			# Send detection result to the visualizer
			for frame_id in sorted_seq:
				# extract drone_id for this frame_id
				drone_id = data_pool[frame_id]["drone_id"]
				# extract plot info for this frame_id
				plot_info = data_pool[frame_id]["plot_info"]
				await self.send_plot_info_and_wait(drone_id, frame_id, plot_info)

	async def send_plot_info_and_wait(self, drone_id, frame_id, plot_info):
		t0_plotinfo_saving = time.time()
		plot_info_key = "plotinfo-drone-%s-frame-%s" % (str(drone_id), str(frame_id))
		redis_set(self.rc, plot_info_key, plot_info, expired=10)  # delete value after 10 seconds
		t1_plotinfo_saving = (time.time() - t0_plotinfo_saving) * 1000
		L.warning('[%s] Latency of Storing Plot info in redisDB (%.3f ms)' %
				  (get_current_time(), t1_plotinfo_saving))
