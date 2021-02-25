from zenoh_service.core.zenoh_net import ZenohNet
from zenoh_service.zenoh_net_publisher import ZenohNetPublisher
import sys
import time
from datetime import datetime
import numpy as np
import cv2
import simplejson as json
from enum import Enum
import logging

###

L = logging.getLogger(__name__)


###


# Define input data
# [1] Data Type: simple Integer / Float / Bool
encoder_format = None
itype = 1
val = 123
###############################################################

# [2] Data Type: Numpy Array (image)
# encoder_format = None
# itype = 2
# root_path = "/home/s010132/devel/eagleeye/data/out1.png"
# val = cv2.imread(root_path)
###############################################################

# [3] Data Type: Numpy Array with structured array format (image + other information)
# itype = 3
# encoder_format = [
# 	('id', 'U10'),
# 	('timestamp', 'f'),
# 	('data', [('flatten', 'i')], (1, 6220800)),
# 	('store_enabled', '?'),
# ]
# root_path = "/home/s010132/devel/eagleeye/data/out1.png"
# img = cv2.imread(root_path)
# img_1d = img.reshape(1, -1)
# val = [('Drone 1', time.time(), img_1d, False)]
###############################################################

# # Scenario 1: Simple Pub/Sub with a single PC
# selector = "/demo/**"

# Scenario 2: Pub/Sub with two hosts
"""
	Simulated scenario:
	- `Host #01` will has IP `192.168.1.110`
	- `Host #01` run `subscriber`
	- `Host #02` run `publisher`
	- Asumming that both hosts are in the multicast network environment
"""
# selector = "/demo/**"
# peer = "tcp/172.18.8.188:7447"
peer = "tcp/localhost:7448"

# configure zenoh service
path = "/eaglestitch/db/zenoh-python-pub"
z_svc = ZenohNetPublisher(
	_path=path, _session_type="PUBLISHER", _peer=peer
)
z_svc.init_connection()

# register and collect publisher object
z_svc.register()
publisher = z_svc.get_publisher()

n_epoch = 5  # total number of publication processes
# for i in range(n_epoch):
while True:
	# publish data
	z_svc.publish(
		_val=val,
		_itype=itype,
		_encoder=encoder_format,
	)

	time.sleep(0.33)

# closing Zenoh publisher & session
z_svc.close_connection(publisher)
