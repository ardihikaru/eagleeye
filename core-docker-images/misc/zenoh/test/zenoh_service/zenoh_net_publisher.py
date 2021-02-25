from zenoh_service.core.zenoh_net import ZenohNet
import sys
import time
from datetime import datetime
import numpy as np
import cv2
import simplejson as json
from enum import Enum
import logging

###

L = logging.getLogger(__name__)


###


class ZenohNetPublisher(ZenohNet):

	class InputDataType(Enum):
		NATIVE_TYPE = 1
		SIMPLE_NUMPY = 2
		COMPLEX_NUMPY = 3

	def __init__(self, _listener=None, _mode="peer", _peer=None, _path=None, _session_type=None):
		super().__init__(_listener=_listener, _mode=_mode, _peer=_peer, _path=_path, _session_type=_session_type)

	def register(self):
		super().register_publisher()

	def get_publisher(self):
		return self.pub

	def _get_encoder(self, _encoder):
		return self.ENCODER if _encoder is None else _encoder

	def _encode_data(self, _val, _itype, _encoder):
		if _itype == self.InputDataType.NATIVE_TYPE.value:
			encoded_data = bytes(json.dumps(_val), encoding='utf8')
		elif _itype == self.InputDataType.SIMPLE_NUMPY.value:
			encoded_data = _val.tobytes()
		elif _itype == self.InputDataType.COMPLEX_NUMPY.value:
			encoder = self._get_encoder(_encoder)
			tagged_data = np.array(_val, dtype=encoder)
			encoded_data = tagged_data.tobytes()
		else:
			# simply convert the data into bytes
			encoded_data = bytes(json.dumps(_val), encoding='utf8')

		return encoded_data

	def publish(self, _val, _itype=1, _encoder=None):
		"""
		_val: The value of the resource to put.
		"""

		# pre-process data before being sent into Zenoh system
		encoded_data = self._encode_data(_val, _itype, _encoder)

		t0_publish = time.time()
		super().publish_data(encoded_data)
		t1_publish = (time.time() - t0_publish) * 1000
		L.warning(('\n[%s] Latency insert data into Zenoh (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_publish)))

	def close_connection(self, _producer=None):
		if _producer is not None:
			_producer.undeclare()
		super().close_connection()


"""
# Usage example
# ---------------

# Define input data
# [1] Data Type: simple Integer / Float / Bool
# encoder_format = None
# itype = 1
# val = 123
###############################################################

# [2] Data Type: Numpy Array (image)
# encoder_format = None
# itype = 2
# root_path = "/home/s010132/devel/eagleeye/data/out1.png"
# val = cv2.imread(root_path)
###############################################################

# [3] Data Type: Numpy Array with structured array format (image + other information)
itype = 3
encoder_format = [
	('id', 'U10'),
	('timestamp', 'f'),
	('data', [('flatten', 'i')], (1, 6220800)),
	('store_enabled', '?'),
]
root_path = "/home/s010132/devel/eagleeye/data/out1.png"
img = cv2.imread(root_path)
img_1d = img.reshape(1, -1)
val = [('Drone 1', time.time(), img_1d, False)]
###############################################################

# configure zenoh service
path = "/demo/example/zenoh-python-pub"
z_svc = ZenohNetPublisher(
	_path=path, _session_type="PUBLISHER"
)
z_svc.init_connection()

# register and collect publisher object
z_svc.register()
publisher = z_svc.get_publisher()

# publish data
z_svc.publish(
	_val=val,
	_itype=itype,
	_encoder=encoder_format,
)

# closing Zenoh publisher & session
z_svc.close_connection(publisher)
"""
