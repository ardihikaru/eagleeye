from scheduler.extractor.zenoh_pubsub.core.zenoh_net import ZenohNet
import sys
import time
from datetime import datetime
import numpy as np
import logging
import asyncio

###

L = logging.getLogger(__name__)


###


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

	def register(self, img_listener):
		super().register_subscriber(img_listener)

	def get_subscriber(self):
		return self.sub

	def close_connection(self, _subscriber=None):
		if _subscriber is not None:
			_subscriber.undeclare()
		if self.z_queryable is not None:
			self.z_queryable.undeclare()
		super().close_connection()
