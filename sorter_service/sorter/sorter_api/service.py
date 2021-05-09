import asab
from enum import Enum
import logging
from ext_lib.utils import get_current_time, pubsub_to_json
from ext_lib.redis.my_redis import MyRedis

###

L = logging.getLogger(__name__)


###


class SorterApiService(asab.Service):

	def __init__(self, app):
		super().__init__(app, "sorter.SorterApiService")

		self.algorithm_svc = app.get_service("sorter.AlgorithmService")

		self.sorter_id = asab.Config["identity"].getint("id")
		self.ch_prefix = asab.Config["identity"]["ch_prefix"]
		self.channel = None

		self.rc = MyRedis(asab.Config).get_rc()

	async def initialize(self, app):
		# build redis channel name
		self.channel = "{}_{}".format(
			self.ch_prefix,
			self.sorter_id,
		)

	async def start_subscription(self):
		consumer = self.rc.pubsub()
		consumer.subscribe([self.channel])
		for item in consumer.listen():
			if isinstance(item["data"], int):
				L.warning("\n[{}] Starting subscription to channel `{}_{}`".format(
						  get_current_time(), self.ch_prefix, self.sorter_id
				))
			else:
				frame_seqs = pubsub_to_json(item["data"])

				print(" >>> Captured Frame Seq: {}".format(frame_seqs))

	# async def sort_and_wait(self, request_json):
	#
	# 	# build data obj
	# 	data_obj = {
	# 		"drone_id": request_json["drone_id"],
	# 		"drone_id": request_json["unsorted_frame_sequences"],
	# 	}
	#
	# 	mbbox_data, selected_pairs = await self.algorithm_svc.calc_mbbox(
	# 		# bbox_data=request_json["bbox_data"],  # DEPRECATED: no need to send this data anymore. we use `det` instead
	# 		det=request_json["det"],
	# 		names=request_json["names"],
	# 		h=request_json["h"],
	# 		w=request_json["w"],
	# 		c=request_json["c"],
	# 		selected_pairs=request_json["selected_pairs"]
	# 	)
	#
	# 	resp_data = {
	# 		"mbbox_data": mbbox_data,
	# 		"selected_pairs": selected_pairs
	# 	}
	#
	# 	return 200, self.StatusCode.REQUEST_OK.value, resp_data
