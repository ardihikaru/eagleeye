from zenoh_service.core.zenoh_native import ZenohNative
import time
from datetime import datetime
import logging

###

L = logging.getLogger(__name__)


###


class ZenohNativePut(ZenohNative):
	def __init__(self, _listener=None, _mode="peer", _path=None, _peer=None, _session_type=None):
		super().__init__(_listener=_listener, _mode=_mode, _path=_path, _peer=_peer, _session_type=_session_type)

	def put(self, val):
		"""
		val: The value of the resource to put.
		"""

		# TODO: pre-process data before being sent into Zenoh system
		# HERE

		t0_publish = time.time()
		super().publish_data(val)
		t1_publish = (time.time() - t0_publish) * 1000
		L.warning(('\n[%s] Latency insert data into Zenoh (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_publish)))

"""
# Usage example
---------------

path = "/demo/example/test3"
value = 123
pub = ZenohNativePut(
	_path=path, _session_type="PUT"
)
pub.init_connection()

# put data
pub.put(value)

# closing Zenoh subscription & session
pub.close_connection()
"""
