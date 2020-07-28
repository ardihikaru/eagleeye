import aiohttp
from ext_lib.redis.translator import redis_set
import logging
import time
from ews.database.config.config_functions import insert_new_data, get_data_by_id, del_data_by_id
from ews.database.config.config import ConfigModel
from ext_lib.utils import get_current_time, get_random_str


###

L = logging.getLogger(__name__)

###


def validate_request_json(request_json):
    valid_list = ["algorithm", "uri", "scalable"]
    if not isinstance(request_json, dict):
        raise aiohttp.web.HTTPBadRequest()

    for key in valid_list:
        if key not in request_json:
            # Log the error
            L.error("Invalid request: {}".format("key `%s` not found." % key))
            raise aiohttp.web.HTTPBadRequest()


def request_to_redisdb(rc, request_json):
    for key, value in request_json.items():
        redis_set(rc, key, value)


def request_to_mongodb(executor, request_json):
    t0_thread = time.time()
    pool_name = "[THREAD-%s]" % get_random_str()
    try:
        kwargs = {
            "pool_name": pool_name,
            "request_json": request_json
        }
        executor.submit(threaded_insertion, **kwargs)
    except:
        print("Somehow we unable to Start the Thread of TaskScheduler")
    t1_thread = (time.time() - t0_thread) * 1000
    print('\n #### [%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_thread))

    # TODO: Save the latency into ElasticSearchDB for the real-time monitoring


def threaded_insertion(pool_name, request_json):
    print(" \n @@@@ threaded_task_scheduler-%s" % pool_name)

    t0_saving_mongo = time.time()
    is_success, config_data, msg = insert_new_data(ConfigModel, request_json)
    t1_saving_mongo = (time.time() - t0_saving_mongo) * 1000
    print('[%s] Latency for Saving data into MongoDB (%.3f ms)' % (get_current_time(), t1_saving_mongo))

    # This is an optional; ONLY for testing purpose! Comment this part later please
    t0_deleting_mongo = time.time()
    _, _ = del_data_by_id(ConfigModel, config_data["id"])
    t1_deleting_mongo = (time.time() - t0_deleting_mongo) * 1000
    print('[%s] Latency for Deleting data into MongoDB (%.3f ms)' % (get_current_time(), t1_deleting_mongo))
    time.sleep(5)
    print(" -- coming back after sleeping in 5 secs ..")