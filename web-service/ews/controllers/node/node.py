"""
   This is a Controller class to manage any action related with /api/nodes endpoint
"""

from ext_lib.utils import json_load_str, get_json_template, get_unprocessable_request_json
from ews.database.node.node import NodeModel
from ews.database.node.node_functions import get_all_data, \
    del_data_by_id, upd_data_by_id, get_data_by_id, insert_new_data
import asab
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import pub
from multidict import MultiDictProxy
from subprocess import Popen
import time
from ext_lib.utils import get_current_time, get_random_str, pop_if_any
from ext_lib.config_builder.config_builder import ConfigBuilder
from concurrent.futures import ThreadPoolExecutor
import os
import signal
import simplejson as json


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
        # Make config file according to this file
        # print(" #### node_data:", node_data)
        builder = ConfigBuilder()
        builder.set_config_path("./../object-detection-service/etc/detection.conf")
        builder.set_default_redis_conf()
        builder.set_default_mongodb_conf()
        # builder.set_default_pubsub_channel_conf(node_id=str(node_data["id"]))
        builder.set_default_yolov3_conf()

        # Add extra information to the accessable API
        root_api = asab.Config["eagleeye:api"]["listen"] + "/api/"
        builder.set_custom_conf("eagleeye:api",
                                {
                                    "node": root_api + "nodes"
                                })

        builder.set_custom_conf("node", node_data)
        builder.set_custom_conf("thread", {"num_executor": "1"})
        builder.set_custom_conf("bbox_config",
                                {
                                    "pih_label_cand": "PiH",
                                    "pih_label": "PiH",
                                    "pih_color": "[198, 50, 13]",  # PiH bbox color: Blue
                                    "person_color": "[191, 96, 165]",  # Person bbox color: Purple
                                    "flag_color": "[100, 188, 70]"  # Flag bbox color: Green
                                })
        # TODO: We need a function to dynamically set the Node URI
        builder.set_custom_conf("zmq", {
            "node_uri": "tcp://127.0.0.1:555" + str(node_data["name"]),  # TODO: Need to be dynamic!
            "node_channel": "node-" + str(node_data["id"]) + "-zmq"
        })
        builder.set_custom_conf("persistence_detection", {
            "persistence_window": 10,
            "tolerance_limit_percentage": 0.3
        })
        builder.create_config()

        # TODO: Once orchestrated with k8s, we no longer use Popen to Deploy each node (Future work)
        process = Popen('python ./../object-detection-service/detection.py -c ./../object-detection-service/etc/detection.conf', shell=True)

        # send data into Scheduler service through the pub/sub
        t0_publish = time.time()
        # print("# send data into Scheduler service through the pub/sub")
        dump_request = json.dumps(node_data)
        pub(self.get_rc(), asab.Config["pubsub:channel"]["node"], dump_request)
        t1_publish = (time.time() - t0_publish) * 1000
        # TODO: Saving latency for scheduler:producer
        print('[%s] Latency for Publishing data into Object Detection Service (%.3f ms)' %
              (get_current_time(), t1_publish))

    def _node_generator(self, node_data):
        t0_thread = time.time()
        pool_name = "[THREAD-%s]" % get_random_str()
        try:
            kwargs = {
                "pool_name": pool_name,
                "node_data": node_data
            }
            self.executor.submit(self._spawn_node, **kwargs)
        except:
            print("\n[%s] Somehow we unable to Start the Thread of NodeGenerator" % get_current_time())
        t1_thread = (time.time() - t0_thread) * 1000
        print('\n[%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_thread))

        # TODO: Save the latency into ElasticSearchDB for the real-time monitoring

    def register(self, node_data):
        msg = "Registration of a new Node is success."

        # Validate
        if "candidate_selection" not in node_data:
            node_data["candidate_selection"] = False
        if "persistence_validation" not in node_data:
            node_data["persistence_validation"] = False

        #  inserting
        is_success, inserted_data, msg = insert_new_data(NodeModel, node_data, msg)

        # TODO: When inserting a new Node succeed, it should spawn an Object Detection module.
        # TODO: To spawn YOLOv3 Module
        if is_success:
            # TODO: Once spwaned, Field `pid` should be updated.
            node_data["id"] = inserted_data["id"]
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

        return get_json_template(is_success, users, total_records, msg)

    def bulk_delete_data_by_id(self, json_data):
        if "id" in json_data:
            if isinstance(json_data["id"], str):
                _, _ = del_data_by_id(NodeModel, json_data["id"], self.rc)
            elif isinstance(json_data["id"], list):
                for user_id in json_data["id"]:
                    _, _ = del_data_by_id(NodeModel, user_id, self.rc)
            else:
                return get_unprocessable_request_json()
            resp_data = {}
            if self.resp_status:
                resp_data = "Deleted ids: {}".format(json_data["id"])
            return get_json_template(True, resp_data, -1, "Deleting data success.")
        else:
            return get_unprocessable_request_json()

    def delete_data_by_id_one(self, _id):
        _, _ = del_data_by_id(NodeModel, _id, self.rc)
        return get_json_template(True, {}, -1, "OK")

    def update_data_by_id(self, _id, json_data):
        is_success, user_data, msg = upd_data_by_id(NodeModel, _id, new_data=json_data)
        return get_json_template(is_success, user_data, -1, msg)

    def get_data_by_id(self, userid):
        is_success, user_data, msg = get_data_by_id(NodeModel, userid)
        return get_json_template(is_success, user_data, -1, msg)
