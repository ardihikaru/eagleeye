from zenoh_pubsub import ZenohPubSub


class ZenohPublisher(ZenohPubSub):
	def __init__(self, _listener=None, _mode="peer", _path=None, _peer=None, _session_type=None):
		super().__init__(_listener=_listener, _mode=_mode, _path=_path, _peer=_peer, _session_type=_session_type)

	def publish(self, val):
		"""
		val = The value of the resource to put.
		"""

		# TODO: pre-process data before being sent into Zenoh system
		# HERE

		super().publish_data(val)


path = "/demo2/example/test2"
value = 123
pub = ZenohPublisher(
	_path=path, _session_type="PUBLISHER"
)
pub.init_connection()

# publish data
pub.publish(value)

# closing Zenoh subscription & session
pub.close_connection()
