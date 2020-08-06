import aiohttp
import logging
import time
from ews.database.config.config_functions import insert_new_data, get_all_data, del_data_by_id, get_data_by_uri, \
	get_data_by_id, upd_data_by_id
from ews.database.config.config import ConfigModel
from ext_lib.utils import get_current_time, get_random_str
from ext_lib.utils import get_json_template

###

L = logging.getLogger(__name__)


###


# def validate_request_json(request_json):
def request_to_config(request_json):
	config = {}
	valid_list = ["algorithm", "uri", "scalable", "stream"]
	if not isinstance(request_json, dict):
		raise aiohttp.web.HTTPBadRequest()

	for key in valid_list:
		if key not in request_json:
			# Log the error
			L.error("Invalid request: {}".format("key `%s` not found." % key))
			raise aiohttp.web.HTTPBadRequest()
		else:
			config[key] = request_json[key]

	# To validate where the image came from
	# TODO: To enable multiple drone streams (Future work)
	# TODO: We need to consider tagging each image with a drone_id, helping the identification phase in Scheduler
	# Currently, only one stream is allowed, if a stream found, return FALSE and notify to delete the current stream
	# // TODO Here
	is_available, _, _ = get_data_by_uri(ConfigModel, request_json["uri"])
	if is_available:
		# Log the error
		L.error("Invalid request: {}".format("This URI is streaming now: `%s`." % request_json["uri"]))
		raise aiohttp.web.HTTPBadRequest()

	return config


# def config_to_redisdb(rc, request_json):
#     for key, value in request_json.items():
#         redis_set(rc, key, value)


def config_to_mongodb(executor, request_json):
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
	print("> >>>> request_json:", request_json)
	is_success, config_data, msg = insert_new_data(ConfigModel, request_json)
	print(" >>>> ", is_success, config_data, msg)
	t1_saving_mongo = (time.time() - t0_saving_mongo) * 1000
	print('[%s] Latency for Saving data into MongoDB (%.3f ms)' % (get_current_time(), t1_saving_mongo))

	# This is an optional; ONLY for testing purpose! Comment this part later please
	t0_deleting_mongo = time.time()
	_, _ = del_data_by_id(ConfigModel, config_data["id"])
	t1_deleting_mongo = (time.time() - t0_deleting_mongo) * 1000
	print('[%s] Latency for Deleting data into MongoDB (%.3f ms)' % (get_current_time(), t1_deleting_mongo))
	# time.sleep(5)
	# print(" -- coming back after sleeping in 5 secs ..")


def get_config_data():
	is_success, config_data, total_records = get_all_data(ConfigModel)

	# TODO: To allow capturing multiple drone video stream & Show multiple live video streams (Future work)
	if is_success:
		# Since currently it only has 1 data..
		return is_success, config_data[0], -1, "OK"
	else:
		return is_success, None, -1, "No video stream found"


def get_config_by_id(_id):
	is_success, config, msg = get_data_by_id(ConfigModel, _id)
	return get_json_template(is_success, config, -1, msg)


def upd_config_by_id(_id, json_data):
	is_success, config, msg = upd_data_by_id(ConfigModel, _id, json_data)
	return get_json_template(is_success, config, -1, msg)


def del_config_by_id(_id):
	is_success, msg = del_data_by_id(ConfigModel, _id)
	return get_json_template(is_success, {}, -1, msg)
