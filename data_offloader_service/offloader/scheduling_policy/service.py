import asab
import logging
import time
from ext_lib.utils import get_current_time
import numpy as np
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_get, redis_set

###

L = logging.getLogger(__name__)


###


class SchedulingPolicyService(asab.Service):
	""" A service to schedule incoming task (image data) """

	def __init__(self, app, service_name="offloader.SchedulingPolicyService"):
		super().__init__(app, service_name)

		# init default value
		self.selected_node_id = 0
		self.max_node = 1
		self.avail_nodes = []
		self.rd = None

	async def initialize(self, app, asab_config=None):
		self.selected_node_id = 0
		self.max_node = 1
		self.avail_nodes = []

		if asab_config is not None:
			self.rd = MyRedis(asab_config)
		else:
			self.rd = MyRedis(asab.Config)

	def _dict2list(self, dict_data):
		list_data = []
		for key, value in dict_data.items():
			tmp_list = [key, value]
			list_data.append(tmp_list)

		return np.asarray(list_data)

	async def initialize_available_nodes(self, avail_nodes):
		t0_shm = time.time()
		for node in avail_nodes:
			redis_key = node["id"] + "_status"  # node_id here starts from `1`

			# node_idx = int(node["name"]) - 1  # node_id here starts from `0`
			# redis_key = str(node_idx) + "_status"
			redis_set(self.rd.get_rc(), redis_key, True)

			self.avail_nodes.append({
				"redis_key": redis_key,
				"value": True
			})

			# L.warning("[DEBUG] Available nodes")
			# L.warning(self.avail_nodes)

		t1_shm = time.time() - t0_shm
		L.warning('Latency [Creating Redis variable] in: (%.5f ms)' % (t1_shm * 1000))

	def find_idle_node(self, max_node=1, sch_policy="round_robin", frame_id=None):
		L.warning("[sync_SCHEDULING_POLICY]: `{}`".format(sch_policy))
		L.warning("[max_node]: `{}`".format(max_node))
		self.max_node = max_node
		if sch_policy == "round_robin":
			self.exec_round_robin(frame_id)
		elif sch_policy == "dynamic_round_robin":
			self.exec_dynamic_round_robin(frame_id)

		# default policy
		else:
			self.exec_dynamic_round_robin(frame_id)

		return self._get_selected_node()

	def _get_selected_node(self):
		return self.selected_node_id

	def exec_dynamic_round_robin(self, frame_id):
		L.warning("[SYNC] I am using Dynamic Round-Robin")
		L.warning("[self.selected_node_id]: `{}`".format(self.selected_node_id))

		# perform a close loop to find an available worker node
		t0_wait_node = time.time()
		self._dynamic_round_robin_wait_until_ready()
		t1_wait_node = (time.time() - t0_wait_node) * 1000

		L.warning('[Frame-{}] Latency [Waiting node to be ready] in: (%.5f ms)'.format(frame_id) % t1_wait_node)

		# Set selected node as busy (idle=False); "0" == False
		self._sync_set_idle_status(self.selected_node_id, False)

	def exec_round_robin(self, frame_id):
		L.warning("[SYNC] I am using Round-Robin")
		self.selected_node_id += 1

		if self.selected_node_id >= self.max_node:
			self.selected_node_id = 0  # Reset

		L.warning("#### ***** checking the status of selected node_id:")
		t0_wait_node = time.time()
		self._round_robin_wait_until_ready(self.selected_node_id)
		t1_wait_node = (time.time() - t0_wait_node) * 1000
		L.warning('[{}] Latency [Waiting node to be ready] in: (%.5f ms)'.format(frame_id) % t1_wait_node)

		# Set selected node as busy (idle=False); "0" == False
		self._sync_set_idle_status(self.selected_node_id, False)

	def _sync_set_idle_status(self, snode_id, status):
		redis_key = self.avail_nodes[snode_id]["redis_key"]
		redis_set(self.rd.get_rc(), redis_key, status)
		self.avail_nodes[snode_id]["value"] = status

	def _round_robin_wait_until_ready(self, snode_id):
		redis_key = self.avail_nodes[snode_id]["redis_key"]
		# L.warning("[sync_DEBUG] redis_key: %s" % str(redis_key))
		# L.warning("[sync_DEBUG] snode_id: %s" % str(snode_id))
		# L.warning("[sync_DEBUG] Redis key (wait until ready): %s" % str(redis_key))
		# L.warning("[sync_DEBUG] Redis > Node STATUS: %s" % str(redis_get(self.rd.get_rc(), redis_key)))
		while not redis_get(self.rd.get_rc(), redis_key):
			continue
		return True

	def _dynamic_round_robin_wait_until_ready(self):
		_node_searching = True
		while _node_searching:
			self.selected_node_id += 1

			if self.selected_node_id >= self.max_node:
				self.selected_node_id = 0  # Reset

			# trying to get node status
			redis_key = self.avail_nodes[self.selected_node_id]["redis_key"]
			# L.warning(" >>> [self.avail_nodes]: `{}`".format(self.avail_nodes))
			# L.warning(" >>> [self.selected_node_id]: `{}`".format(self.selected_node_id))
			# L.warning(" >>> [redis_key]: `{}`".format(redis_key))
			# L.warning(" >>> [redis_key VALUE]: `{}`\n\n".format(redis_get(self.rd.get_rc(), redis_key)))
			if redis_get(self.rd.get_rc(), redis_key):
				_node_searching = False
