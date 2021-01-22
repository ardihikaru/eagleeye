from zenoh_pubsub import ZenohPubSub
import sys
import logging

###

L = logging.getLogger(__name__)


###


def listener(change):
	L.warning("[ZENOH][Subscription listener] received {:?} for {} : {} with timestamp {}"
	      .format(change.kind, change.path, '' if change.value is None else change.value.get_content(),
	              change.timestamp))


class ZenohSubscriber(ZenohPubSub):
	def __init__(self, _listener=None, _mode="peer", _peer=None, _selector=None, _session_type=None):
		super().__init__(_listener=_listener, _mode=_mode, _peer=_peer, _selector=_selector, _session_type=_session_type)

	def register(self):
		super().register_subscriber(listener)

	def get_subscriber(self):
		return self.sub

	def close_connection(self, _subscriber):
		_subscriber.close()
		super().close_connection()


selector = "/demo2/**"
sub = ZenohSubscriber(
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
