from zenoh_service.core.zenoh_native import ZenohNative
import sys
import time
from datetime import datetime
import logging

###

L = logging.getLogger(__name__)


###


def listener(change):
	# print(">>> change.value:", change.value, type(change.value.get_content()), type(float(change.value.get_content())))
	print("Consumed Value: {}".format(change.value.get_content()))
	# t1_recv = (time.time() - change.value.get_content()) * 1000
	# L.warning(('\n[%s] Latency E2E receive data (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_recv)))
	L.warning("[ZENOH][Subscription listener] received {:?} for {} : {} with timestamp {}"
	      .format(change.kind, change.path, '' if change.value is None else change.value.get_content(),
	              change.timestamp))

	# print(">> [Storage listener] Received ('{}': '{}')"
	#       .format(change.res_name, change.payload.decode("utf-8")))
	# store[sample.res_name] = (change.payload, change.data_info)


class ZenohNativeSubscriber(ZenohNative):
	def __init__(self, _listener=None, _mode="peer", _peer=None, _selector=None, _session_type=None):
		super().__init__(_listener=_listener, _mode=_mode, _peer=_peer, _selector=_selector, _session_type=_session_type)

	def register(self):
		super().register_subscriber(listener)

	def get_subscriber(self):
		return self.sub

	def close_connection(self, _subscriber=None):
		if _subscriber is not None:
			_subscriber.close()
		super().close_connection()


"""
# Usage example
---------------

selector = "/demo/**"
sub = ZenohNativeSubscriber(
	_selector=selector, _session_type="SUBSCRIBER"
)
sub.init_connection()

sub.register()
subscriber = sub.get_subscriber()
L.warning("[ZENOH] Press q to stop...")
c = '\0'
while c != 'q':
	c = sys.stdin.read(1)

# closing Zenoh subscription & session
sub.close_connection(subscriber)
"""