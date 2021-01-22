from pubsub import PubSub
import logging
import zenoh
from zenoh.net import config, SubInfo, Reliability, SubMode, Sample, resource_name
from zenoh.net.queryable import STORAGE
from enum import Enum

###

L = logging.getLogger(__name__)


###


class ZenohNet(PubSub):
	"""
	Implementation of Zenoh-net

	Default input parameter for Zenoh Subscriber is:
		(listener=None, mode='peer', peer=None, selector='/demo2/**')

	Default input parameter for Zenoh Publisher is:
		(listener=None, mode='peer', path='/demo2/example/test', peer=None, value='Hello World')
	"""

	class ZenohMode(Enum):
		PEER = "peer"
		CLIENT = "client"

	class SessionType(Enum):
		SUBSCRIBER = "SUBSCRIBER"
		PUBLISHER = "PUBLISHER"

	def __init__(self, _listener=None, _mode="peer", _peer=None, _selector=None, _path=None, _session_type=None,
	             _network_enabled=False):
		self.listener = _listener  # Locators to listen on.
		self.mode = _mode  # The zenoh session mode.
		self.peer = _peer  # Peer locators used to initiate the zenoh session.
		self.selector = _selector  # The selection of resources to subscribe.
		self.path = _path  # The name of the resource to put.
		self.session_type = self._get_session_type(_session_type)  # Type of Zenoh connection
		self.network_enabled = self.network_enabled  # Type of Zenoh network mode: enabled/disabled

		# setup configuration
		self.conf = {"mode": self.mode}
		if self.peer is not None:
			self.conf["peer"] = ",".join(args.peer)
		if self.listener is not None:
			self.conf["listener"] = ",".join(args.listener)

		self.workspace = None
		self.z_session = None
		self.sub_info = None

		self.pub = None
		self.sub = None

	def _get_session_type(self, _type):
		if _type.upper() == self.SessionType.PUBLISHER.value:
			return self.SessionType.PUBLISHER.value
		elif _type.upper() == self.SessionType.SUBSCRIBER.value:
			return self.SessionType.SUBSCRIBER.value
		else:
			return None

	def init_connection(self):
		# initiate logging
		zenoh.init_logger()

		L.warning("[ZENOH] Openning session...")
		self.z_session = zenoh.net.open(self.conf)

		self.sub_info = SubInfo(Reliability.Reliable, SubMode.Push)

		L.warning("Declaring Subscriber on '{}'...".format(selector))
		self.sub = self.z_session.declare_subscriber(self.selector, self.sub_info, listener)

		L.warning("[ZENOH] Create New workspace...")
		self.workspace = self.z_session.workspace()

	def _configure_zenoh_session(self):
		pass

	def _configure_zenoh_net_session(self):
		pass

	def close_connection(self):
		self.z_session.close()
		L.warning("[ZENOH] `{}` session has been closed".format(self.session_type))

	def register_subscriber(self, listener):
		L.warning("[ZENOH] Registering new consumer")
		self.sub = self.workspace.subscribe(self.selector, listener)

	def publish_data(self, val):
		L.warning("[ZENOH] Publish data")
		self.workspace.put(self.path, val)
