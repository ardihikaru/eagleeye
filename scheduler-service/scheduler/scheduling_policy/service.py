import asab
import logging
import imagezmq
import time
from ext_lib.utils import get_current_time
import requests
import numpy as np
# from multiprocessing import shared_memory
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
        # self.avail_nodes = {}
        self.avail_nodes = []

        self.rd = MyRedis(asab.Config)

        print(" >>>> DEFAULT self.selected_node_id:", self.selected_node_id)

    def _dict2list(self, dict_data):
        list_data = []
        for key, value in dict_data.items():
            tmp_list = [key, value]
            list_data.append(tmp_list)

        return np.asarray(list_data)

    async def init_available_nodes(self, avail_nodes):
        # self.avail_nodes = np.asarray(avail_nodes)
        # avail_nodes = np.asarray(avail_nodes)

        t0_shm = time.time()
        for node in avail_nodes:
            # create shm-based node information
            # node_info = np.asarray([node])
            # print("### node:", node)
            # print("### node ID:", node["id"])
            # node_info = np.asarray(self._dict2list(node))

            redis_key = node["id"] + "_status"
            redis_set(self.rd.get_rc(), redis_key, True)

            # node_info = np.asarray(self._dict2list({
            #     "id": node["id"],
            #     "idle": int(bool(node["idle"])),
            #     "name": node["name"]
            # }))
            # # print("### node_info:", node_info)
            # # shm = shared_memory.SharedMemory(create=True, size=avail_nodes.nbytes, name="available_nodes")
            # t0_load_shm = time.time()
            # try:
            #     shm = shared_memory.SharedMemory(create=True, size=node_info.nbytes, name=node["id"])
            # except:  # error due to SHM is exist
            #     t0_delete_shm = time.time()
            #     # load existing shm instead
            #     shm = shared_memory.SharedMemory(name=node["id"])
            #
            #     # Optional
            #     # delete existing shm
            #     shm.close()
            #     shm.unlink()
            #     t1_delete_shm = time.time() - t0_delete_shm
            #     print('\nLatency [Delete shm variable] in: (%.5f ms)' % (t1_delete_shm * 1000))
            #
            #     # build shm
            #     shm = shared_memory.SharedMemory(create=True, size=node_info.nbytes, name=node["id"])
            #
            # t1_load_shm = time.time() - t0_load_shm
            # print('\nLatency [Create empty SHM] in: (%.5f ms)' % (t1_load_shm * 1000))
            #
            # # create a NumPy array backed by shared memory
            # t0_assign_shm = time.time()
            # np_node = np.ndarray(node_info.shape, dtype=node_info.dtype, buffer=shm.buf)
            # np_node[:] = node_info[:]  # Copy the original data into shared memory
            # t1_assign_shm = time.time() - t0_assign_shm
            # print('\nLatency [Assign img value into shm value] in: (%.5f ms)' % (t1_assign_shm * 1000))

            # self.avail_nodes[redis_key] = True
            self.avail_nodes.append({
                "redis_key": redis_key,
                "value": True
            })
            # self.avail_nodes.append(redis_key)

        # print("### FINALL: ", self.avail_nodes)

        t1_shm = time.time() - t0_shm
        # print('\nLatency [Creating shm variable] in: (%.5f ms)' % (t1_shm * 1000))
        print('\nLatency [Creating Redis variable] in: (%.5f ms)' % (t1_shm * 1000))

        # # Testing stored data
        # for shm_node in self.avail_nodes:
        #     print(">>>>>>> shm_node=", type(shm_node), shm_node)  # harusnya type SHM
        #     print(">>>>>>> IDLE Status=", self._get_idle_status(shm_node))
        #
        # print(">>>>>> DATA:", self.avail_nodes[0])
        # for i in range(len(self.avail_nodes[0])):
        #     print("WOOWW:", self.avail_nodes[0][i][0])

        # TODO: To unlink and close the SHM once done or Service is stopped
        # shm.close()
        # shm.unlink()

    async def schedule(self, max_node=1, sch_policy="round_robin"):
        self.max_node = max_node
        if sch_policy == "round_robin":
            await self.round_robin()
        else:
            await self.round_robin()

        return self._get_selected_node()

    def _get_selected_node(self):
        return self.selected_node_id

    async def round_robin(self):
        # print(" >>>> NOW self.selected_node_id:", self.selected_node_id)
        print("I am using Round-Robin")
        self.selected_node_id += 1

        if self.selected_node_id >= self.max_node:
            self.selected_node_id = 0  # Reset

        # print("#### ***** check the status of selected node_id:")
        t0_wait_node = time.time()
        await self._wait_until_ready(self.selected_node_id)
        t1_wait_node = time.time() - t0_wait_node
        print('\nLatency [Waiting node to be ready] in: (%.5fs)' % (t1_wait_node * 1000))

        # Set selected node as busy (idle=False); "0" == False
        # self.avail_nodes[self.selected_node_id]["idle"] = "0"
        await self._set_idle_status(self.selected_node_id, False)
        # try:
        #     await self._set_idle_status(self.selected_node_id, False)
        # except Exception as e:
        #     print("ERROR set idle status=", e)

    async def _set_idle_status(self, snode_id, status):
        redis_key = self.avail_nodes[snode_id]["redis_key"]
        redis_set(self.rd.get_rc(), redis_key, status)
        self.avail_nodes[snode_id]["value"] = status

        # print(">>>>>> DATA:", self.avail_nodes[0])
        # for i in range(len(self.avail_nodes[0])):
        #     print("WOOWW:", self.avail_nodes[0][i][0])
        #
        # print("LEN:", len(self.avail_nodes), snode_id)
        # print(">>>> DATA ajaa:", self.avail_nodes[snode_id])
        # for i in range(len(self.avail_nodes[snode_id])):
        #     print(">>>> DATA:", self.avail_nodes[snode_id][i], self.avail_nodes[0][i][0])
        #     if self.avail_nodes[0][i][0] == "idle":
        #         self.avail_nodes[0][i][1] = status

    # def _get_idle_status(self, node_info):
        # for key_value in node_info:
        #     if key_value[0] == "idle":
        #         return bool(int(key_value[1]))

    async def _wait_until_ready(self, snode_id):
        redis_key = self.avail_nodes[snode_id]["redis_key"]
        # print("### @@@@ _wait_until_ready ...", redis_get(self.rd.get_rc(), redis_key))
        # while not self.avail_nodes[snode_id]["idle"]:
        # while not self._get_idle_status(self.avail_nodes[snode_id]):
        while not redis_get(self.rd.get_rc(), redis_key):
            continue
        return True
