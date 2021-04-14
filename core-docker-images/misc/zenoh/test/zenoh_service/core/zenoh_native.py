from zenoh_service.core.service_abc import ServiceABC
import logging
import zenoh
from zenoh import Zenoh
from enum import Enum

###

L = logging.getLogger(__name__)


###


class ZenohNative(ServiceABC):
	"""
	A higher level API providing the same abstractions as the zenoh-net API in a simpler and more data-centric oriented
	manner as well as providing all the building blocks to create a distributed storage. The zenoh layer is aware of
	the data content and can apply content-based filtering and transcoding.
	(source: http://zenoh.io/docs/getting-started/key-concepts/)

	Available functionalities:
		[1] put         : push live data to the matching subscribers and storages. (equivalent of zenoh-net write)
		[2] subscribe   : subscriber to live data. (equivalent of zenoh-net subscribe)
		[3] get         : get data from the matching storages and evals. (equivalent of zenoh-net query)
		[4] storage     : the combination of a zenoh-net subscriber to listen for live data to store and a zenoh-net
						  queryable to reply to matching get requests.
		[5] eval        : an entity able to reply to get requests. Typically used to provide data on demand or
						  build a RPC system. (equivalent of zenoh-net queryable)

	Implemented scenarios:
	1. Zenoh SUBSCRIBER
		Sample input: listener=None, mode='peer', peer=None, selector='/demo2/**'
	2. Zenoh PUT
		Sample input: listener=None, mode='peer', path='/demo2/example/test', peer=None, value='Hello World'
	3. Zenoh GET
		Sample input: listener=None, mode='peer', peer=None, selector='/demo/example/**'
	"""

	class ZenohMode(Enum):
		PEER = "peer"
		CLIENT = "client"

	class SessionType(Enum):
		SUBSCRIBER = "SUBSCRIBER"
		PUT = "PUT"
		GET = "GET"

	def __init__(self, _listener=None, _mode="peer", _peer=None, _selector=None, _path=None, _session_type=None):
		super().__init__()
		self.listener = _listener  # Locators to listen on.
		self.mode = _mode  # The zenoh session mode.
		self.peer = _peer  # Peer locators used to initiate the zenoh session.
		self.selector = _selector  # The selection of resources to subscribe.
		self.path = _path  # The name of the resource to put.
		self.session_type = self._get_session_type(_session_type)  # Type of Zenoh connection

		# setup configuration
		self.conf = {"mode": self.mode}
		if self.peer is not None:
			self.conf["peer"] = self.peer
		if self.listener is not None:
			self.conf["listener"] = self.listener

		self.workspace = None
		self.z_session = None

		self.pub = None
		self.sub = None

	def _get_session_type(self, _type):
		if _type.upper() == self.SessionType.PUT.value:
			return self.SessionType.PUT.value
		elif _type.upper() == self.SessionType.SUBSCRIBER.value:
			return self.SessionType.SUBSCRIBER.value
		elif _type.upper() == self.SessionType.GET.value:
			return self.SessionType.GET.value
		else:
			return None

	def init_connection(self):
		# initiate logging
		# zenoh.init_logger()

		L.warning("[ZENOH] Openning session...")
		self.z_session = Zenoh(self.conf)

		L.warning("[ZENOH] Create New workspace...")
		self.workspace = self.z_session.workspace()

	def close_connection(self, _subscriber=None):
		self.z_session.close()
		L.warning("[ZENOH] `{}` session has been closed".format(self.session_type))

	def register_subscriber(self, listener):
		L.warning("[ZENOH] Registering new consumer")
		self.sub = self.workspace.subscribe(self.selector, listener)

	def register_publisher(self):
		pass  # nothing to do here

	def publish_data(self, val):
		L.warning("[ZENOH] Publish data")
		self.workspace.put(self.path, val)
