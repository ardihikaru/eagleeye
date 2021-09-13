import asab
from ext_lib.utils import get_json_template
import aiohttp
from ews.controllers.stream_reader.functions import request_to_config, config_to_mongodb, get_config_data, \
    get_config_by_id, upd_config_by_id, del_config_by_id
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import pub
import time
from ext_lib.utils import get_current_time
from concurrent.futures import ThreadPoolExecutor
import simplejson as json
import logging

###

L = logging.getLogger(__name__)


###


class StreamReader:
    def __init__(self):
        self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))
        self.redis = MyRedis(asab.Config)

    def read(self, request_json):
        # Validate input
        # print(request_json)
        t0_validator = time.time()
        config = request_to_config(request_json)
        t1_validator = (time.time() - t0_validator) * 1000
        # print('[%s] Latency for Request Validation (%.3f ms)' % (get_current_time(), t1_validator))
        L.warning('[%s] Latency for Request Validation (%.3f ms)' % (get_current_time(), t1_validator))

        # send data into Scheduler service through the pub/sub
        t0_publish = time.time()
        L.warning("Sending config information to [Offloader service] through the Redis pub/sub")
        config["timestamp"] = time.time()  # To verify the communication latency
        dump_request = json.dumps(config)
        pub(self.redis.get_rc(), asab.Config["pubsub:channel"]["scheduler"], dump_request)
        t1_publish = (time.time() - t0_publish) * 1000
        config.pop("timestamp")  # removed, since it is a temporary key
        # TODO: Saving latency for scheduler:producer
        L.warning('[%s] Latency for Publishing data (%.3f ms)' % (get_current_time(), t1_publish))

        # save input into mongoDB through thread process (optional)
        if config.get("save_to_db", False):
            L.warning("# save input into mongoDB through thread process")
            # remove identifier `key` [save_to_db]
            config.pop("save_to_db")
            config_to_mongodb(self.executor, config)
        else:
            L.warning("# NO NEED to save input into mongoDB through thread process")

        return aiohttp.web.json_response(get_json_template(True, request_json, -1, "OK"))

    async def get_data(self):
        is_success, config, total, msg = get_config_data()
        return aiohttp.web.json_response(get_json_template(is_success, config, total, msg))

    def delete_data_by_id_one(self, _id):
        return del_config_by_id(_id)

    def update_data_by_id(self, _id, json_data):
        return upd_config_by_id(_id, json_data)

    def get_data_by_id(self, _id):
        return get_config_by_id(_id)
