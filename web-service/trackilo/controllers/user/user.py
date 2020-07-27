"""
   This is a Controller class to manage any action related with /api/users endpoint
"""

from werkzeug.security import generate_password_hash, check_password_hash
from trackilo.addons.utils import json_load_str, get_json_template, get_unprocessable_request_json, get_synced_date
from trackilo.addons.database_blacklist.blacklist_helpers import (
    revoke_current_token
)
from trackilo.database.user.user import UserModel
from trackilo.database.user.user_functions import get_all_data, store_jwt_data, get_data_by_username, \
    del_data_by_id, upd_data_by_id, get_data_by_id, insert_new_data
import asab
from trackilo.addons.redis.my_redis import MyRedis
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

    def set_status_code(self, code):
        self.status_code = code

    def set_resp_status(self, status):
        self.resp_status = status

    def set_resp_data(self, json_data):
        self.resp_data = json_data

    def set_msg(self, msg):
        self.msg = msg

    def set_password(self, passwd):
        self.password_hash = generate_password_hash(passwd)

    def is_password_match(self, password):
        return check_password_hash(self.password_hash, password)

    def revokesExistedToken(self, encoded_token=None):
        if encoded_token:
            revoke_current_token(self.rc, asab.Config, encoded_token)

    def do_logout(self, encoded_token=None):
        self.revokesExistedToken(encoded_token)
        return get_json_template(response=True, results=-1, total=-1, message="Logout Success.")

    def __validate_register_data(self, json_data):
        is_input_valid = True
        if "name" not in json_data:
            return False, "Name should not be EMPTY."

        if "username" not in json_data:
            return False, "Username should not be EMPTY."

        if "email" not in json_data:
            return False, "Email should not be EMPTY."

        if "password" not in json_data:
            return False, "Password should not be EMPTY."

        if "password_confirm" not in json_data:
            return False, "Password Confirmation is EMPTY."

        if json_data["password"] != json_data["password_confirm"]:
            return False, "Password Confirmation miss match with Password."

        if is_input_valid:
            is_id_exist, _ = get_data_by_username(UserModel, json_data["username"])
            if is_id_exist:
                return False, "Username `%s` have been used." % json_data["username"]

        return True, None

    def trx_register(self, json_data):
        is_valid, msg = self.__validate_register_data(json_data)
        self.set_resp_status(is_valid)
        self.set_msg(msg)

        if is_valid:
            msg = "Registration is success. Now, you can login into our system."
            self.set_password(json_data["password"])
            json_data["password"] = self.password_hash

            #  inserting
            is_valid, inserted_data, msg = insert_new_data(UserModel, json_data, msg)

            # clean up sensitive data
            json_data.pop("password")
            # json_data.pop("password_confirm")

            self.set_msg(msg)

        self.set_resp_data(json_data)

    def register(self, json_data):
        self.trx_register(json_data)
        return get_json_template(response=self.resp_status, results=self.resp_data, total=-1, message=self.msg)

    def __validate_login_data(self, json_data):
        self.set_resp_status(False)
        self.set_resp_data(json_data)
        is_input_valid = True
        if "username" not in json_data:
            is_input_valid = False
            self.set_msg("Username should not be EMPTY.")

        if "password" not in json_data:
            is_input_valid = False
            self.set_msg("Password should not be EMPTY.")

        if is_input_valid:
            is_id_exist, user_data = get_data_by_username(UserModel, json_data["username"])
            if is_id_exist:
                self.password_hash = user_data["password"]
                if self.is_password_match(json_data["password"]):  # check password
                    self.set_resp_status(is_id_exist)
                    self.set_msg("User data FOUND.")

                    access_token, access_token_expired = store_jwt_data(json_data)

                    # set resp_data
                    resp_data = {"access_token": access_token,
                                 "access_token_expired": access_token_expired,
                                 "username": json_data["username"]}
                    self.set_resp_data(resp_data)
                else:
                    self.set_msg("Incorrect Password.")
            else:
                self.set_msg("Incorrect Username.")

    def validate_user(self, json_data):
        self.__validate_login_data(json_data)
        return get_json_template(response=self.resp_status, results=self.resp_data, total=-1, message=self.msg)

    def trx_get_users(self, get_args=None):
        is_valid, users, self.total_records = get_all_data(UserModel, get_args)
        self.set_resp_status(is_valid)
        self.set_msg("Fetching data failed.")
        if is_valid:
            self.set_msg("Collecting data success.")

        self.set_resp_data(users)

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

    def get_users(self, get_args=None):
        get_args = self.__extract_get_args(get_args)
        self.trx_get_users(get_args=get_args)
        return get_json_template(response=self.resp_status, results=self.resp_data, message=self.msg,
                                 total=self.total_records)

    def trx_del_data_by_id(self, userid):
        is_valid, user_data, msg = get_data_by_id(UserModel, userid)
        if is_valid:
            is_valid, msg = del_data_by_id(UserModel, userid)
        self.set_resp_status(is_valid)
        self.set_msg(msg)
        if is_valid:
            self.set_msg("Deleting data success.")

    def delete_data_by_id(self, json_data):
        if "id" in json_data:
            if isinstance(json_data["id"], str):
                self.trx_del_data_by_id(json_data["id"])
            elif isinstance(json_data["id"], list):
                for user_id in json_data["id"]:
                    self.trx_del_data_by_id(user_id)
            else:
                return get_unprocessable_request_json()
            resp_data = {}
            if self.resp_status:
                resp_data = "Deleted ids: {}".format(json_data["id"])
            return get_json_template(response=self.resp_status, results=resp_data, total=-1, message=self.msg)
        else:
            return get_unprocessable_request_json()

    def delete_data_by_id_one(self, _id):
        self.trx_del_data_by_id(_id)
        return get_json_template(response=self.resp_status, results=self.resp_data, total=-1, message=self.msg)

    def trx_upd_data_by_id(self, userid, json_data):
        is_valid, user_data, msg = upd_data_by_id(UserModel, userid, new_data=json_data)
        self.set_resp_status(is_valid)
        self.set_msg(msg)
        if is_valid:
            self.set_msg("Updating data success.")

        self.set_resp_data(user_data)

    def update_data_by_id(self, _id, json_data):
        self.trx_upd_data_by_id(_id, json_data)
        return get_json_template(response=self.resp_status, results=self.resp_data, total=-1, message=self.msg)

    def trx_get_data_by_id(self, userid):
        is_valid, user_data, _ = get_data_by_id(UserModel, userid)
        self.set_resp_status(is_valid)
        self.set_msg("Fetching data failed.")
        if is_valid:
            self.set_msg("Collecting data success.")

        self.set_resp_data(user_data)

    def get_data_by_id(self, userid):
        self.trx_get_data_by_id(userid)
        return get_json_template(response=self.resp_status, results=self.resp_data, total=-1, message=self.msg)
