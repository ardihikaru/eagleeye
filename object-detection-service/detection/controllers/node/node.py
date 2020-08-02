from detection.database.node.node import NodeModel
from detection.database.node.node_functions import upd_data_by_id, get_data_by_id, del_data_by_id
import asab
from ext_lib.redis.my_redis import MyRedis


class Node(MyRedis):
    def __init__(self):
        super().__init__(asab.Config)
        self.status_code = 200
        self.resp_status = None
        self.resp_data = None
        self.total_records = 0
        self.msg = None
        self.password_hash = None

    def update_data_by_id(self, _id, json_data):
        is_success, user_data, msg = upd_data_by_id(NodeModel, _id, new_data=json_data)
        return is_success, user_data, -1, msg

    def delete_data_by_id(self, _id):
        is_success, _ = del_data_by_id(NodeModel, _id)
        return is_success, {}, -1, "OK"

    def get_data_by_id(self, userid):
        is_success, user_data, msg = get_data_by_id(NodeModel, userid)
        return is_success, user_data, -1, msg
