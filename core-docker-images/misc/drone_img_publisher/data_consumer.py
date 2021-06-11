from zenoh_lib.zenoh_net_subscriber import ZenohNetSubscriber
import sys
import cv2
import time
from datetime import datetime
import logging
import numpy as np
from zenoh_lib.functions import extract_compressed_tagged_img
try:
	import imagezmq
except Exception as e:
	pass

###

L = logging.getLogger(__name__)


###

# Setup ZMQ Sender
enable_zmq = False
# enable_zmq = True
if enable_zmq:
	# uri = 'tcp://127.0.0.1:5550'
	uri = 'tcp://*:5548'
	sender = imagezmq.ImageSender(connect_to=uri, REQ_REP=False)


def listener_v2(consumed_data):
	"""
	Expected data model:
	[
		[img_data],  # e.g. 1000
		[drone_id],  # extra tag 01
		[t0_part_1],  # extra tag 02
		[t0_part_2],  # extra tag 03
		[total_number_of_tag],
		[tagged_data_len],  # total array size: `img_data` + `total_number_of_tag` + 1
	]
	"""
	img_info, latency_data = extract_compressed_tagged_img(consumed_data)

	global enable_zmq
	global uri
	global sender

	# print(" --- ")
	#
	# cv.imshow("window_title", img_info["img"])
	#
	# print(" SELESAI")

	# decompressed_img = img_info["img"]
	# identifier = latency_data["decoding_payload"]

	# cv2.imwrite("decompressed_img.jpg", decompressed_img)
	# cv2.imwrite("decompressed_img_{}.jpg".format(str(identifier)), decompressed_img)

	# print(" >>> enable_zmq:", enable_zmq)

	if enable_zmq:
		frame_id = int(img_info["frame_id"])
		print(">>> Sending frame-{} ..".format(frame_id))
		t0_zmq = time.time()
		zmq_id = str(frame_id) + "-" + str(t0_zmq)
		sender.send_image(zmq_id, img_info["img"])
		t1_zmq = (time.time() - t0_zmq) * 1000
		L.warning('Latency [Send imagezmq] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))

"""
	Simulated scenario:
	- `Host #01` will has IP `192.168.1.110`
	- `Host #01` run `subscriber`
	- `Host #02` run `publisher`
	- Asumming that both hosts are in the multicast network environment
"""
selector = "/eagleeye/svc/**"
# listener = "tcp/140.113.86.92:7446"
# listener = "tcp/192.168.1.232:7446"
# listener = "tcp/192.168.1.10:7446"
listener = "tcp/localhost:7446"

sub = ZenohNetSubscriber(
	_selector=selector, _session_type="SUBSCRIBER", _listener=listener
)
sub.init_connection()

# sub.register()
sub.register(listener_v2)
# subscriber = sub.get_subscriber()
subscriber = sub.get_subscriber()
L.warning("[ZENOH] Press q to stop...")
c = '\0'
while c != 'q':
	c = sys.stdin.read(1)

# # closing Zenoh subscription & session
sub.close_connection(subscriber)
