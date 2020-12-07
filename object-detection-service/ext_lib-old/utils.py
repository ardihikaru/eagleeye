"""
   This file provide every common function needed by all Classes of Functions
"""

import json
from datetime import datetime, timedelta
import string
import random
import cv2
import numpy as np


def get_current_time():
	return datetime.now().strftime("%H:%M:%S")


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
