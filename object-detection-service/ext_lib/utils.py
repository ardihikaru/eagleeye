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

def letterbox(img, new_shape=(416, 416), color=(128, 128, 128), auto=True, scaleFill=False, scaleup=True,
			  interp=cv2.INTER_AREA):
	# Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
	shape = img.shape[:2]  # current shape [height, width]

	if isinstance(new_shape, int):
		new_shape = (new_shape, new_shape)

	# Scale ratio (new / old)
	r = max(new_shape) / max(shape)
	if not scaleup:  # only scale down, do not scale up (for better test mAP)
		r = min(r, 1.0)

	# Compute padding
	ratio = r, r  # width, height ratios
	new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
	dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
	if auto:  # minimum rectangle
		dw, dh = np.mod(dw, 32), np.mod(dh, 32)  # wh padding
	elif scaleFill:  # stretch
		dw, dh = 0.0, 0.0
		new_unpad = new_shape
		ratio = new_shape[0] / shape[1], new_shape[1] / shape[0]  # width, height ratios

	dw /= 2  # divide padding into 2 sides
	dh /= 2

	if shape[::-1] != new_unpad:  # resize
		img = cv2.resize(img, new_unpad, interpolation=interp)  # INTER_AREA is better, INTER_LINEAR is faster
	top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
	left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
	img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
	return img, ratio, (dw, dh)
