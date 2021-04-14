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

    def __init__(self, app, service_name="scheduler.SchedulingPolicyService"):
        super().__init__(app, service_name)
        self.selected_node_id = 0
        self.max_node = 1
        self.avail_nodes = []
        self.rd = MyRedis(asab.Config)

    def _dict2list(self, dict_data):
        list_data = []
        for key, value in dict_data.items():
            tmp_list = [key, value]
            list_data.append(tmp_list)

        return np.asarray(list_data)

    async def init_available_nodes(self, avail_nodes):
        t0_shm = time.time()
        for node in avail_nodes:
            redis_key = node["id"] + "_status"
            redis_set(self.rd.get_rc(), redis_key, True)

            self.avail_nodes.append({
                "redis_key": redis_key,
                "value": True
            })

            L.warning("[DEBUG] Available nodes")
            L.warning(self.avail_nodes)

        t1_shm = time.time() - t0_shm
        L.warning('\nLatency [Creating Redis variable] in: (%.5f ms)' % (t1_shm * 1000))

    def sync_schedule(self, max_node=1, sch_policy="round_robin"):
        self.max_node = max_node
        if sch_policy == "round_robin":
            self.sync_round_robin()
        else:
            self.sync_round_robin()

        return self._get_selected_node()

    async def schedule(self, max_node=1, sch_policy="round_robin"):
        self.max_node = max_node
        if sch_policy == "round_robin":
            await self.round_robin()
        else:
            await self.round_robin()

        return self._get_selected_node()

    def _get_selected_node(self):
        return self.selected_node_id

    def sync_round_robin(self):
        L.warning("I am using Round-Robin")
        self.selected_node_id += 1

        if self.selected_node_id >= self.max_node:
            self.selected_node_id = 0  # Reset

        L.warning("#### ***** checking the status of selected node_id:")
        t0_wait_node = time.time()
        self._sync_wait_until_ready(self.selected_node_id)
        t1_wait_node = (time.time() - t0_wait_node) * 1000
        # print('\nLatency [Waiting node to be ready] in: (%.5f ms)' % t1_wait_node)
        L.warning('\nLatency [Waiting node to be ready] in: (%.5f ms)' % t1_wait_node)

        # Set selected node as busy (idle=False); "0" == False
        self._sync_set_idle_status(self.selected_node_id, False)

    async def round_robin(self):
        # print("I am using Round-Robin")
        L.warning("I am using Round-Robin")
        self.selected_node_id += 1

        if self.selected_node_id >= self.max_node:
            self.selected_node_id = 0  # Reset

        L.warning("#### ***** checking the status of selected node_id:")
        t0_wait_node = time.time()
        await self._wait_until_ready(self.selected_node_id)
        # self._wait_until_ready(self.selected_node_id)
        t1_wait_node = (time.time() - t0_wait_node) * 1000
        # print('\nLatency [Waiting node to be ready] in: (%.5f ms)' % t1_wait_node)
        L.warning('\nLatency [Waiting node to be ready] in: (%.5f ms)' % t1_wait_node)

        # Set selected node as busy (idle=False); "0" == False
        # self.avail_nodes[self.selected_node_id]["idle"] = "0"
        await self._set_idle_status(self.selected_node_id, False)

    def _sync_set_idle_status(self, snode_id, status):
        redis_key = self.avail_nodes[snode_id]["redis_key"]
        redis_set(self.rd.get_rc(), redis_key, status)
        self.avail_nodes[snode_id]["value"] = status

    async def _set_idle_status(self, snode_id, status):
        redis_key = self.avail_nodes[snode_id]["redis_key"]
        redis_set(self.rd.get_rc(), redis_key, status)
        self.avail_nodes[snode_id]["value"] = status

    def _sync_wait_until_ready(self, snode_id):
        redis_key = self.avail_nodes[snode_id]["redis_key"]
        L.warning("[DEBUG] snode_id: %s" % str(snode_id))
        L.warning("[DEBUG] Redis key (wait until ready): %s" % str(redis_key))
        L.warning("[DEBUG] Redis > Node STATUS: %s" % str(redis_get(self.rd.get_rc(), redis_key)))
        while not redis_get(self.rd.get_rc(), redis_key):
            continue
        return True

    async def _wait_until_ready(self, snode_id):
        redis_key = self.avail_nodes[snode_id]["redis_key"]
        L.warning("[DEBUG] snode_id: %s" % str(snode_id))
        L.warning("[DEBUG] Redis key (wait until ready): %s" % str(redis_key))
        L.warning("[DEBUG] Redis > Node STATUS: %s" % str(redis_get(self.rd.get_rc(), redis_key)))
        while not redis_get(self.rd.get_rc(), redis_key):
            continue
        return True
