from zenoh_service.core.zenoh_net import ZenohNet
import sys
import time
from datetime import datetime
import numpy as np
import logging

###

L = logging.getLogger(__name__)


###


def listener(consumed_data):
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


def query_handler(query):
	L.warning(">> [Query handler   ] Handling '{}?{}'"
          .format(query.res_name, query.predicate))
	replies = []
	for stored_name, (data, data_info) in store.items():
		if resource_name.intersect(query.res_name, stored_name):
			query.reply(Sample(stored_name, data, data_info))


class ZenohNetSubscriber(ZenohNet):
	def __init__(self, _listener=None, _mode="peer", _peer=None, _selector=None, _session_type=None):
		super().__init__(_listener=_listener, _mode=_mode, _peer=_peer, _selector=_selector, _session_type=_session_type)

	def register(self, listener_v2):
		# super().register_subscriber(listener)
		super().register_subscriber(listener_v2)

	def get_subscriber(self):
		return self.sub

	def close_connection(self, _subscriber=None):
		if _subscriber is not None:
			_subscriber.undeclare()
		if self.z_queryable is not None:
			self.z_queryable.undeclare()
		super().close_connection()


"""
# Usage example
# ---------------

selector = "/demo/**"
sub = ZenohNetSubscriber(
	_selector=selector, _session_type="SUBSCRIBER"
)
sub.init_connection()

sub.register()
subscriber = sub.get_subscriber()
L.warning("[ZENOH] Press q to stop...")
c = '\0'
while c != 'q':
	c = sys.stdin.read(1)

# # closing Zenoh subscription & session
sub.close_connection(subscriber)
"""
