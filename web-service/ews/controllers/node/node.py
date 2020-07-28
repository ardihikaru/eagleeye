"""
   This is a Controller class to manage any action related with /api/nodes endpoint
"""

from ext_lib.utils import json_load_str, get_json_template, get_unprocessable_request_json
from ews.database.node.node import NodeModel
from ews.database.node.node_functions import get_all_data, get_data_by_consumer, \
    del_data_by_id, upd_data_by_id, get_data_by_id, insert_new_data
import asab
from ext_lib.redis.my_redis import MyRedis
from multidict import MultiDictProxy


class User(MyRedis):
    def __init__(self):
        super().__init__(asab.Config)
        self.status_code = 200
        self.resp_status = None
        self.resp_data = None
        self.total_records = 0
        self.msg = None
        self.password_hash = None

    def register(self, json_data):
        msg = "Registration of a new Node is success."
        #  inserting
        is_success, inserted_data, msg = insert_new_data(NodeModel, json_data, msg)
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
                # self.del_data_by_id(json_data["id"])
            elif isinstance(json_data["id"], list):
                for user_id in json_data["id"]:
                    _, _ = del_data_by_id(NodeModel, user_id)
                    # self.del_data_by_id(user_id)
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
        # self.trx_get_data_by_id(userid)
        is_success, user_data, msg = get_data_by_id(NodeModel, userid)
        return get_json_template(is_success, user_data, -1, msg)
