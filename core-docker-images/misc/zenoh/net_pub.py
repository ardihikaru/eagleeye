# Copyright (c) 2017, 2020 ADLINK Technology Inc.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ADLINK zenoh team, <zenoh@adlink-labs.tech>

import sys
import time
import argparse
import itertools
import zenoh
from zenoh.net import config

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog='zn_pub',
    description='zenoh-net pub example')
parser.add_argument('--mode', '-m', dest='mode',
                    default='peer',
                    choices=['peer', 'client'],
                    type=str,
                    help='The zenoh session mode.')
parser.add_argument('--peer', '-e', dest='peer',
                    metavar='LOCATOR',
                    action='append',
                    type=str,
                    help='Peer locators used to initiate the zenoh session.')
parser.add_argument('--listener', '-l', dest='listener',
                    metavar='LOCATOR',
                    action='append',
                    type=str,
                    help='Locators to listen on.')
parser.add_argument('--path', '-p', dest='path',
                    default='/demo/example/zenoh-python-pub',
                    type=str,
                    help='The name of the resource to publish.')
parser.add_argument('--value', '-v', dest='value',
                    default='Pub from Python!',
                    type=str,
                    help='The value of the resource to publish.')

args = parser.parse_args()
conf = { "mode": args.mode }
if args.peer is not None:
    conf["peer"] = ",".join(args.peer)
if args.listener is not None:
    conf["listener"] = ",".join(args.listener)
path = args.path
value = args.value

# zenoh-net code  --- --- --- --- --- --- --- --- --- --- ---

# initiate logging
zenoh.init_logger()

print("Openning session...")
session = zenoh.net.open(conf)

print("Declaring Resource " + path)
rid = session.declare_resource(path)
print(" => RId {}".format(rid))

print("Declaring Publisher on {}".format(rid))
publisher = session.declare_publisher(rid)

val = {"1": 123, "kucing": 100.0}

from utils import str_encryptor
import numpy as np
import cv2
import time
root_path = "/home/s010132/devel/eagleeye/data/out1.png"
image = cv2.imread(root_path)
img_1d = image.reshape(1, -1)

img_info = [('Drone 1', False, time.time(), img_1d)]
# print(img_info)
data = np.array(img_info,
                 dtype=[('id', 'U10'),
                        ('store_enabled', '?'),
                        ('timestamp', 'f'),
                        ('image', [('pixel', 'i')], (1, 6220800))
                        ]
                 )

# data = {
# 	"id": str(1),
# 	"data": image,
# 	"store_enabled": "False",
# 	"timestamp": str(time.time())
# }
# print(" TYPE: ", type(image))
# print("SHAPE: ", image.shape)

# zer = np.zeros((1, 2), dtype=int)
# zer[0][0] = 111
# zer[0][1] = image
# print("SHAPE zer: ", zer.shape)
# print(zer)

# img2 = image.reshape(image.shape + (1,))
# print("SHAPE img2: ", img2.shape)
# print("img2 DATA BARU: ", img2[])

# import time
# from datetime import datetime
# import logging
#
# ###
#
# L = logging.getLogger(__name__)
#
#
# ###
#
# t0_encode_img = time.time()
# bytes_img = image.tobytes()
# t1_encode_img = (time.time() - t0_encode_img) * 1000
# L.warning(('\n[%s] Latency encode Image numpy (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_encode_img)))

# data = {
# 	"id": str(1),
# 	"data": bytes_img,
# 	"store_enabled": "False",
# 	"timestamp": str(time.time())
# }
# data = np.asarray([1, bytes_img, False, time.time()])
# print("TYPE : ", type(data), data.shape)
# print(data[0].decode(), type(int(data[0])))
# print(data[2].decode(), type(bool(data[2])))
# print(data[3].decode(), type(float(data[3])))
# print(type(data[1]))
# print("dtype >>>>> ", type(data.dtype))

# print(" --- DIISNI ..")
# # deserialized_bytes = np.frombuffer(data[1])
# deserialized_bytes = np.frombuffer(data[1], dtype=np.int8)
# # deserialized_bytes = np.frombuffer(image.tobytes())
# # print(type(deserialized_bytes))
# # print(deserialized_bytes)
# # deserialized_img = np.reshape(deserialized_bytes, newshape=(1080, 1920, 3))
# deserialized_img = np.reshape(deserialized_bytes, newshape=(1080, 1920, 3))
# print(type(deserialized_img))
# print(deserialized_img.shape)

# ### COBA
# sent = data.tobytes()
# print(sent)
# d_bytes = np.frombuffer(sent, dtype=np.bytes)
# d_data = np.reshape(d_bytes, newshape=(4,))
# print(d_data.shape)
# print(d_data[0])

print(">>> itertools.count():", itertools.count())
for idx in itertools.count():
    time.sleep(1)
    print("sending ..")
    # buf = "[{:4d}] {}".format(idx, value)
    # buf = "[{:4d}] {}".format(idx, val)
    # buf = "[{:4d}] {}".format(idx, image)
    # buf = "[{:4d}] {}".format(idx, data)
    # buf = "{}".format(data)
    # import simplejson as json
    # buf = "{}".format(json.dumps(data))
    # print("Writing Data ('{}': '{}')...".format(rid, buf))
    # session.write(rid, bytes(buf, encoding='utf8'))
    # session.write(rid, bytes(data, encoding='utf8'))
    session.write(rid, image.tobytes())  # sending only image
    # session.write(rid, data.tobytes())  # sending tuple data (tagged images)
    # session.write(rid, bytes_img)

publisher.undeclare()
session.close()
