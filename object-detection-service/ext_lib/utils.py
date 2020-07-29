"""
   This file provide every common function needed by all Classes of Functions
"""

import json
from datetime import datetime, timedelta
import string
import random
import cv2
import numpy as np


def mongo_list_to_dict(mongo_resp):
	"""
		Converts List data from MongoDB response into a dictionary
	"""

	result = []
	list_data = json.loads(mongo_resp)
	for data in list_data:
		data = mongo_dict_to_dict(data, is_dict=True)
		result.append(data)
	return result


def mongo_dict_to_dict(mongo_resp, is_dict=False):
	"""
		Casts Fields from MongoDB response into simpler dictionary; Casted keys are:
		1. From `["id"]["$oid"]` into ["id"]
		2. From `["created_at"]["$date"]` into ["created_at"]
		3. From `["updated_at"]["$date"]` into ["updated_at"]
	"""

	if is_dict:
		data = mongo_resp
	else:
		data = json.loads(mongo_resp)

	data["id"] = data["_id"]["$oid"]
	data.pop("_id")

	if "created_at" in data and \
			data["created_at"] is not None and \
			"$date" in data["created_at"]:
		data["created_at"] = datetime.fromtimestamp(int(str(data["created_at"]["$date"])[:-3])).strftime("%Y-%m-%d, "
																										 "%H:%M:%S")

	if "updated_at" in data and \
			data["updated_at"] is not None and \
			"$date" in data["updated_at"]:
		data["updated_at"] = datetime.fromtimestamp(int(str(data["updated_at"]["$date"])[:-3])).strftime("%Y-%m-%d, "
																										 "%H:%M:%S")

	if "sync_datetime" in data and \
			data["sync_datetime"] is not None and \
			"$date" in data["sync_datetime"]:
		data["sync_datetime"] = datetime.fromtimestamp(int(str(data["sync_datetime"]["$date"])[:-3])). \
			strftime("%Y-%m-%d, %H:%M:%S")

	return data


def pop_if_any(data, key):
	try:
		if key in data:
			data.pop(key)
	except:
		pass
	return data


def get_current_time():
	return datetime.now().strftime("%H:%M:%S")


def get_random_str(k=5):
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))


def pubsub_to_json(json_data):
	data = None
	try:
		data = json.loads(json_data)
	except:
		pass
	return data
