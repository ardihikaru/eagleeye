from zenoh_pubsub import ZenohPubSub
import time
from datetime import datetime
import logging

###

L = logging.getLogger(__name__)


###


class ZenohPublisher(ZenohPubSub):
	def __init__(self, _listener=None, _mode="peer", _path=None, _peer=None, _session_type=None):
		super().__init__(_listener=_listener, _mode=_mode, _path=_path, _peer=_peer, _session_type=_session_type)

	def publish(self, val):
		"""
		val = The value of the resource to put.
		"""

		# TODO: pre-process data before being sent into Zenoh system
		# HERE

		t0_publish = time.time()
		L.warning("TIME ZERO: {}".format(t0_publish))
		# super().publish_data(val)
		super().publish_data(t0_publish)
		t1_publish = (time.time() - t0_publish) * 1000
		L.warning(('\n[%s] Latency insert data into Zenoh (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_publish)))


path = "/demo/example/test3"
value = 123
pub = ZenohPublisher(
	_path=path, _session_type="PUBLISHER"
)
pub.init_connection()

# publish data
pub.publish(value)

# closing Zenoh subscription & session
pub.close_connection()
