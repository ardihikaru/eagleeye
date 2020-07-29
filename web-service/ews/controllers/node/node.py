"""
   This is a Controller class to manage any action related with /api/nodes endpoint
"""

from ext_lib.utils import json_load_str, get_json_template, get_unprocessable_request_json
from ews.database.node.node import NodeModel
from ews.database.node.node_functions import get_all_data, \
    del_data_by_id, upd_data_by_id, get_data_by_id, insert_new_data
import asab
from ext_lib.redis.my_redis import MyRedis
from multidict import MultiDictProxy
from subprocess import Popen
import time
from ext_lib.utils import get_current_time, get_random_str
from concurrent.futures import ThreadPoolExecutor
import os
import signal


class Node(MyRedis):
    def __init__(self):
        super().__init__(asab.Config)
        self.status_code = 200
        self.resp_status = None
        self.resp_data = None
        self.total_records = 0
        self.msg = None
        self.password_hash = None
        self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

    def _spawn_node(self, pool_name, node_data):
        print("I am spawning a new node now.")

        pid = os.getpid()
        print(" --- _spawn_node PID", pid)

        # time.sleep(5)
        # print(" ---- AFTER WAITING in 5 secs")
        # TODO: Once orchestrated with k8s, we no longer use Popen to Deploy each node (Future work)
        process = Popen('python ./../object-detection-service/detection.py -c ./../object-detection-service/etc/detection.conf', shell=True)
        print(" --- CHILD ID", process.pid)
        time.sleep(5)

        print(" ---- TYPE process.pid:", type(process.pid))
        os.kill(process.pid, signal.SIGTERM)  # or signal.SIGKILL
        # os.kill(pid, signal.SIGTERM)  # or signal.SIGKILL
        print(" --- killed [PID=%s] after 5 seconds" % str(process.pid))

    def _node_generator(self, node_data):

        pid = os.getpid()
        print(" --- PARENT PID", pid)

        t0_thread = time.time()
        pool_name = "[THREAD-%s]" % get_random_str()
        try:
            kwargs = {
                "pool_name": pool_name,
                "node_data": node_data
            }
            self.executor.submit(self._spawn_node, **kwargs)
        except:
            print("Somehow we unable to Start the Thread of NodeGenerator")
        t1_thread = (time.time() - t0_thread) * 1000
        print('\n #### [%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_thread))

        # TODO: Save the latency into ElasticSearchDB for the real-time monitoring


    def register(self, node_data):
        msg = "Registration of a new Node is success."
        #  inserting
        is_success, inserted_data, msg = insert_new_data(NodeModel, node_data, msg)

        # TODO: When inserting a new Node succeed, it should spawn an Object Detection module.
        # TODO: To spawn YOLOv3 Module
        self._node_generator(node_data)

        return get_json_template(response=is_success, results=inserted_data, total=-1, message=msg)

    def __extract_get_args(self, get_args):
        if get_args is not None:
            if not isinstance(get_args, MultiDictProxy):
                if "filter" in get_args:
                    get_args["filter"] = json_load_str(get_args["filter"], "dict")
                if "range" in get_args:
                    get_args["range"] = json_load_str(get_args["range"], "list")
                if "sort" in get_args:
                    get_args["sort"] = json_load_str(get_args["sort"], "list")

        return get_args

    def get_data(self, get_args=None):
        get_args = self.__extract_get_args(get_args)
        is_success, users, total_records = get_all_data(NodeModel, get_args)
        msg = "Fetching data failed."
        if is_success:
            msg = "Collecting data success."

        return get_json_template(is_success, users, msg, total_records)

    def bulk_delete_data_by_id(self, json_data):
        if "id" in json_data:
            if isinstance(json_data["id"], str):
                _, _ = del_data_by_id(NodeModel, json_data["id"])
            elif isinstance(json_data["id"], list):
                for user_id in json_data["id"]:
                    _, _ = del_data_by_id(NodeModel, user_id)
            else:
                return get_unprocessable_request_json()
            resp_data = {}
            if self.resp_status:
                resp_data = "Deleted ids: {}".format(json_data["id"])
            return get_json_template(True, resp_data, -1, "Deleting data success.")
        else:
            return get_unprocessable_request_json()

    def delete_data_by_id_one(self, _id):
        _, _ = del_data_by_id(NodeModel, _id)
        return get_json_template(True, {}, -1, "OK")

    def update_data_by_id(self, _id, json_data):
        is_success, user_data, msg = upd_data_by_id(NodeModel, _id, new_data=json_data)
        return get_json_template(is_success, user_data, -1, msg)

    def get_data_by_id(self, userid):
        is_success, user_data, msg = get_data_by_id(NodeModel, userid)
        return get_json_template(is_success, user_data, -1, msg)
