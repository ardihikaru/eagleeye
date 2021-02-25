from zenoh_service.core.service_abc import ServiceABC
import logging
import zenoh
from zenoh.net import config, SubInfo, Reliability, SubMode, Sample, resource_name
from zenoh.net.queryable import STORAGE
from enum import Enum

###

L = logging.getLogger(__name__)


###


class ZenohNet(ServiceABC):
	"""
	A higher level API providing the same abstractions as the zenoh-net API in a simpler and more data-centric oriented
	manner as well as providing all the building blocks to create a distributed storage. The zenoh layer is aware of
	the data content and can apply content-based filtering and transcoding.
	(source: http://zenoh.io/docs/getting-started/key-concepts/)

	Available functionalities:
		[1] write : push live data to the matching subscribers.
		[2] subscribe : subscriber to live data.
		[3] query : query data from the matching queryables.
		[4] queryable : an entity able to reply to queries.

	Implemented scenarios:
	1. Zenoh SUBSCRIBER with STORAGE (Queryable)
		Sample input: listener=None, mode='peer', peer=None, selector='/demo/example/**'
	2. Zenoh PUBLISHER
		Sample input: listener=None, mode='peer', path='/demo2/example/test', peer=None, value='Hello World'
	3. Zenoh GET
		Sample input: listener=None, mode='peer', peer=None, selector='/demo/example/**'
	"""

	class ZenohMode(Enum):
		PEER = "peer"
		CLIENT = "client"

	class SessionType(Enum):
		SUBSCRIBER = "SUBSCRIBER"
		PUBLISHER = "PUBLISHER"

	# set default encoder
	ENCODER = [
		('id', 'U10'),
		('timestamp', 'f'),
		('data', [('flatten', 'i')], (1, 6220800)),
		('store_enabled', '?'),
	]

	def __init__(self, _listener=None, _mode="peer", _peer=None, _selector=None, _path=None, _session_type=None,
	             type_numpy=False, tagged_data=False):
		super().__init__()
		self.listener = _listener  # Locators to listen on.
		self.mode = _mode  # The zenoh session mode.
		self.peer = _peer  # Peer locators used to initiate the zenoh session.
		self.selector = _selector  # The selection of resources to subscribe.
		self.path = _path  # The name of the resource to put.
		self.session_type = self._get_session_type(_session_type)  # Type of Zenoh connection
		self.type_numpy = type_numpy  # Expected type of the extracted data

		if type_numpy:  # to be assigned only when the type is a numpy array
			self.tagged_data = tagged_data  # When tagged, data will be an encoded into list
			"""
			Sample data of `tagged_data`
			[
				<id: String>,
				<timestamp: Float>,
				<data: Numpy array>,
				<other1: some_data_type>
			]
			"""

		# setup configuration
		self.conf = {"mode": self.mode}
		if self.peer is not None:
			self.conf["peer"] = self.peer
		if self.listener is not None:
			self.conf["listener"] = self.listener

		self.z_session = None
		self.z_sub_info = None
		self.z_queryable = None
		self.z_rid = None

		self.pub = None
		self.sub = None

	def _get_session_type(self, _type):
		if _type.upper() == self.SessionType.SUBSCRIBER.value:
			return self.SessionType.SUBSCRIBER.value
		elif _type.upper() == self.SessionType.PUBLISHER.value:
			return self.SessionType.PUBLISHER.value
		else:
			return None

	def init_connection(self):
		# initiate logging
		zenoh.init_logger()

		L.warning("[ZENOH] Openning session...")
		self.z_session = zenoh.net.open(self.conf)

		self.z_sub_info = SubInfo(Reliability.Reliable, SubMode.Push)

	def close_connection(self, _subscriber=None):
		self.z_session.close()
		L.warning("[ZENOH] `{}` session has been closed".format(self.session_type))

	def register_subscriber(self, listener, queryable=False):
		L.warning("[ZENOH] Registering new consumer")
		self.sub = self.z_session.declare_subscriber(self.selector, self.z_sub_info, listener)

		if queryable:
			L.warning("[ZENOH] Declaring Queryable on '{}'...".format(selector))
			self.z_queryable = self.z_session.declare_queryable(
				self.selector, STORAGE, query_handler)

	def register_publisher(self):
		L.warning("[ZENOH] Registering new producer")
		self.z_rid = self.z_session.declare_resource(self.path)
		self.pub = self.z_session.declare_publisher(self.z_rid)

	def publish_data(self, encoded_val):
		L.warning("[ZENOH] Publish data")
		self.z_session.write(self.z_rid, encoded_val)
