import aiounittest
import asab
import asyncio
from scheduler_service.scheduler.scheduling_policy.service import SchedulingPolicyService
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_get, redis_set
import logging
import time

###

L = logging.getLogger(__name__)


###


class TestSchedulingPolicyService(aiounittest.AsyncTestCase, SchedulingPolicyService):
	""" Testing Scheduling Policy Service """

	def setUp(self):
		""" Set up testing objects """
		self.max_node_data = 4
		self.asab_config = {
			"redis": {
				"hostname": "localhost",
				"port": 6379,
				"password": "",
				"db": 0,
			}
		}

		self.sch_policy_01 = "round_robin"
		self.sch_policy_02 = "dynamic_round_robin"

		self.rd = MyRedis(self.asab_config)

	def generate_dummy_node_info(self, node_id):
		return {
			# "id": "id_{}".format(node_id),
			"id": "{}".format(node_id),
			"name": "name_{}".format(node_id),
			"channel": "channel_{}".format(node_id),
			"consumer": "consumer_{}".format(node_id),
			"candidate_selection": True,
			"persistence_validation": True,
		}

	async def build_avail_nodes_obj(self):
		avail_nodes_obj = []
		for i in range(self.max_node_data):
			node_id = i + 1
			node_info = self.generate_dummy_node_info(node_id)
			avail_nodes_obj.append(node_info)

		return avail_nodes_obj

	async def async_add(self, x, y, delay=0.1):
		await asyncio.sleep(delay)
		return x + y

	async def test_await_async_add(self):
		ret = await self.async_add(1, 5)
		self.assertEqual(ret, 6)

	async def test_schedule_rr(self):
		avail_nodes = await self.build_avail_nodes_obj()
		await self.initialize(self, self.asab_config)
		await self.init_available_nodes(avail_nodes)

		# set default current node_id
		self.selected_node_id = 2

		# set default `max_node`
		self.max_node = self.max_node_data

		sel_node_id = self.sync_schedule(max_node=self.max_node, sch_policy=self.sch_policy_01)
		L.warning("[RESULT] Selected NodeID = `{}`".format(sel_node_id))

	async def test_schedule_drr_no_obstacle_test_one(self):
		avail_nodes = await self.build_avail_nodes_obj()
		await self.initialize(self, self.asab_config)
		await self.init_available_nodes(avail_nodes)

		# set next node_ids (=`2`) as busy
		busy_nodes = [2]  # index 1-th, 2-th, 3-th; only index 0-th is available
		await self.init_available_nodes(avail_nodes, busy_nodes)

		# set default current node_id
		self.selected_node_id = 1

		# set default `max_node`
		self.max_node = self.max_node_data

		# should resulted index 3-th
		sel_node_id = self.sync_schedule(max_node=self.max_node, sch_policy=self.sch_policy_02)
		self.assertEqual(3, sel_node_id)
		L.warning("[RESULT] Selected NodeID = `{}`".format(sel_node_id))

	async def test_schedule_drr_no_obstacle_test_two(self):
		avail_nodes = await self.build_avail_nodes_obj()
		await self.initialize(self, self.asab_config)
		await self.init_available_nodes(avail_nodes)

		# set node_id (=`3`) as busy
		busy_nodes = [3]  # index 1-th, 2-th, 3-th; only index 0-th is available
		await self.init_available_nodes(avail_nodes, busy_nodes)

		# set default current node_id
		self.selected_node_id = 2

		# set default `max_node`
		self.max_node = self.max_node_data

		# should resulted index 0-th
		sel_node_id = self.sync_schedule(max_node=self.max_node, sch_policy=self.sch_policy_02)
		self.assertEqual(0, sel_node_id)
		L.warning("[RESULT] Selected NodeID = `{}`".format(sel_node_id))

	async def test_schedule_drr_one_obstacle_test_one(self):
		avail_nodes = await self.build_avail_nodes_obj()
		await self.initialize(self, self.asab_config)

		# set next node_ids (=`1, 2, 3`) as busy
		busy_nodes = [1, 2, 3]  # index 1-th, 2-th, 3-th; only index 0-th is available
		await self.init_available_nodes(avail_nodes, busy_nodes)

		# set default current node_id
		self.selected_node_id = 1  # index 1-th

		# set default `max_node`
		self.max_node = self.max_node_data

		# should resulted index 0-th
		sel_node_id = self.sync_schedule(max_node=self.max_node, sch_policy=self.sch_policy_02)
		self.assertEqual(0, sel_node_id)
		L.warning("[RESULT] Selected NodeID = `{}`".format(sel_node_id))

	async def test_schedule_drr_one_obstacle_test_two(self):
		avail_nodes = await self.build_avail_nodes_obj()
		await self.initialize(self, self.asab_config)

		# set next node_id (=`2`) as busy
		busy_nodes = [2]  # index 1-th, 2-th, 3-th; only index 0-th is available
		await self.init_available_nodes(avail_nodes, busy_nodes)

		# set default current node_id
		self.selected_node_id = 1  # index 1-th

		# set default `max_node`
		self.max_node = self.max_node_data

		# should resulted index 3-th
		sel_node_id = self.sync_schedule(max_node=self.max_node, sch_policy=self.sch_policy_02)
		self.assertEqual(3, sel_node_id)
		L.warning("[RESULT] Selected NodeID = `{}`".format(sel_node_id))

	async def test_schedule_drr_one_obstacle_test_three(self):
		avail_nodes = await self.build_avail_nodes_obj()
		await self.initialize(self, self.asab_config)

		# set next node_id (=`1, 2, 3`) as busy
		busy_nodes = [1, 2, 3]  # index 1-th, 2-th, 3-th; only index 0-th is available
		await self.init_available_nodes(avail_nodes, busy_nodes)

		# set default current node_id
		self.selected_node_id = 0  # index 0-th

		# set default `max_node`
		self.max_node = self.max_node_data

		# should resulted index 3-th
		sel_node_id = self.sync_schedule(max_node=self.max_node, sch_policy=self.sch_policy_02)
		self.assertEqual(0, sel_node_id)
		L.warning("[RESULT] Selected NodeID = `{}`".format(sel_node_id))

	# override function!
	async def init_available_nodes(self, avail_nodes, busy_nodes=None):
		if busy_nodes is None:
			busy_nodes = []

		t0_shm = time.time()
		for node in avail_nodes:
			# redis_key = node["id"] + "_status"  # node_id here starts from `1`

			node_idx = int(node["id"]) - 1  # node_id here starts from `0`
			redis_key = str(node_idx) + "_status"

			# if int(node["id"]) in busy_nodes:
			if node_idx in busy_nodes:
				# L.warning("> Set Node `{}` as BUSY.".format(node["id"]))
				L.warning("> Set Node `{}-th` as BUSY.".format(node_idx))
				redis_set(self.rd.get_rc(), redis_key, False)

				self.avail_nodes.append({
					"redis_key": redis_key,
					"value": False
				})
			else:
				redis_set(self.rd.get_rc(), redis_key, True)

				self.avail_nodes.append({
					"redis_key": redis_key,
					"value": True
				})

		t1_shm = time.time() - t0_shm
		L.warning('\nLatency [Creating Redis variable] in: (%.5f ms)' % (t1_shm * 1000))


if __name__ == '__main__':
	unittest.main()
