from scheduler.database.node.node import NodeModel
from scheduler.database.node.node_functions import upd_data_by_id, get_data_by_id, del_data_by_id, get_all_data
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

    def get_data(self):
        is_success, users, total_records = get_all_data(NodeModel, None)
        msg = "Fetching data failed."
        if is_success:
            msg = "Collecting data success."

        return is_success, users, msg, total_records

    def update_data_by_id(self, _id, json_data):
        is_success, user_data, msg = upd_data_by_id(NodeModel, _id, new_data=json_data)
        return is_success, user_data, -1, msg

    def delete_data_by_id(self, _id):
        is_success, _ = del_data_by_id(NodeModel, _id)
        return is_success, {}, -1, "OK"

    def get_data_by_id(self, userid):
        is_success, user_data, msg = get_data_by_id(NodeModel, userid)
        return is_success, user_data, -1, msg
