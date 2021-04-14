from zenoh_service.core.zenoh_net import ZenohNet
from zenoh_service.zenoh_net_subscriber import ZenohNetSubscriber
import sys
import time
from datetime import datetime
import logging
import numpy as np

###

L = logging.getLogger(__name__)


###


def listener_v2(consumed_data):
	# # ####################### For tuple data
	# t0_decoding = time.time()
	# encoder_format = [
	# 	('id', 'U10'),
	# 	('timestamp', 'f'),
	# 	('data', [('flatten', 'i')], (1, 6220800)),
	# 	('store_enabled', '?'),
	# ]
	# deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=encoder_format)
	#
	# t1_decoding = (time.time() - t0_decoding) * 1000
	# L.warning(
	#     ('\n[%s] Latency deserialized_bytes (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
	#
	# t0_decoding = time.time()
	# img_ori = deserialized_bytes["data"]["flatten"][0].reshape(1080, 1920, 3)
	# print(">>> img_ori SHAPE:", img_ori.shape)
	#
	# t1_decoding = (time.time() - t0_decoding) * 1000
	# L.warning(
	#     ('\n[%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
	# # ######################## END for tuple data
	# # ########################

	############
	############ For IMAGE ONLY
	t0_decoding = time.time()
	deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=np.int8)
	t1_decoding = (time.time() - t0_decoding) * 1000
	L.warning(
	    ('\n[%s] Latency load ONLY numpy image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))


	t0_decoding = time.time()
	deserialized_img = np.reshape(deserialized_bytes, newshape=(1080, 1920, 3))
	print(">>> img_ori SHAPE:", deserialized_img.shape)
	t1_decoding = (time.time() - t0_decoding) * 1000
	L.warning(
	    ('\n[%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))
	############ END For IMAGE ONLY
	############

	# L.warning("Consumed Value: {}".format(consumed_data.payload))
	# store[consumed_data.res_name] = (consumed_data.payload, consumed_data.data_info)


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
selector = "/eagleeye/img/**"
# listener = "tcp/172.18.8.188:7447"
listener = "tcp/localhost:7447"

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
