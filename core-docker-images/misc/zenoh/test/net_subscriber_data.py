from zenoh_service.core.zenoh_net import ZenohNet
from zenoh_service.zenoh_net_subscriber import ZenohNetSubscriber
import sys
import time
from datetime import datetime
import logging
import numpy as np

###

L = logging.getLogger(__name__)


###


def listener_v2(consumed_data):
	print(" --- DISINI ...")
	L.warning("Consumed Value: {}".format(consumed_data.payload))
	# store[consumed_data.res_name] = (consumed_data.payload, consumed_data.data_info)


# # Scenario 1: Simple Pub/Sub with a single PC
# selector = "/demo/**"

# Scenario 2: Pub/Sub with two hosts
"""
	Simulated scenario:
	- `Host #01` will has IP `192.168.1.110`
	- `Host #01` run `subscriber`
	- `Host #02` run `publisher`
	- Asumming that both hosts are in the multicast network environment
"""
selector = "/eaglestitch/db/**"
# listener = "tcp/172.18.8.188:7447"
listener = "tcp/localhost:7448"

sub = ZenohNetSubscriber(
	_selector=selector, _session_type="SUBSCRIBER", _listener=listener
)
sub.init_connection()

# sub.register()
sub.register(listener_v2)
# subscriber = sub.get_subscriber()
subscriber = sub.get_subscriber()
L.warning("[ZENOH] Press q to stop...")
c = '\0'
while c != 'q':
	c = sys.stdin.read(1)

# # closing Zenoh subscription & session
sub.close_connection(subscriber)
