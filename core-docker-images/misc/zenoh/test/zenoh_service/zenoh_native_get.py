from zenoh_service.core.zenoh_native import ZenohNative
import numpy as np
import time
from datetime import datetime
import logging

###

L = logging.getLogger(__name__)


###


class ZenohNativeGet(ZenohNative):
	def __init__(self, _listener=None, _mode="peer", _selector=None, _peer=None, _session_type=None,
	             type_image=False, tagged_image=False):
		super().__init__(_listener=_listener, _mode=_mode, _selector=_selector, _peer=_peer, _session_type=_session_type)
		self.type_image = type_image
		self.tagged_image = tagged_image

	def get(self, count=False):
		"""
		selector: The selection of resources to get.
		"""

		t0_get = time.time()

		if count:
			print(">>>> count: {}".format(count))
			total = len(self.workspace.get(self.selector))
			print("Total data: {}".format(total))
		else:
			for data in self.workspace.get(self.selector):
				print("Data path: {}".format(data.path))
				# print('  {} : {}  (encoding: {} , timestamp: {})'.format(
				# 	data.path, data.value.get_content(), data.value.encoding_descr(), data.timestamp))

				if self.type_image and self.tagged_image:
					# data is an encoded image;
					print(" --- type: {}; {}; {}".format(
						type(data.value.get_content()[0]),
						data.value.get_content()[0],
						data.value.get_content()[1]
					))
					# self._extract_normal_img(data.value.get_content())
				elif self.type_image and not self.tagged_image:
					# data is an encoded image and tagged with extra information;
					self._extract_tagged_img(data.value.get_content())
				else:
					print("Data: {}".format(data.value.get_content()))

		t1_get = (time.time() - t0_get) * 1000
		L.warning(('\n[%s] Latency get data from Zenoh (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_get)))

	def _extract_normal_img(self, img_data):
		t0_decoding = time.time()
		deserialized_bytes = np.frombuffer(img_data, dtype=np.int8)
		t1_decoding = (time.time() - t0_decoding) * 1000
		L.warning(
			('\n[%s] Latency load ONLY numpy image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

		t0_decoding = time.time()
		deserialized_img = np.reshape(deserialized_bytes, newshape=(1080, 1920, 3))
		t1_decoding = (time.time() - t0_decoding) * 1000
		L.warning(
			('\n[%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

	def _extract_tagged_img(self, img_data):
		t0_decoding = time.time()
		deserialized_bytes = np.frombuffer(img_data, dtype=[('id', 'U10'),
		                                      ('store_enabled', '?'),
		                                      ('timestamp', 'f'),
		                                      ('image', [('pixel', 'i')], (1, 6220800))
		                                      ])

		t1_decoding = (time.time() - t0_decoding) * 1000
		L.warning(
		    ('\n[%s] Latency deserialized_bytes (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

		t0_decoding = time.time()
		img_original = deserialized_bytes["image"]["pixel"][0].reshape(1080, 1920, 3)
		print(">>> img_original SHAPE:", img_original.shape)

		t1_decoding = (time.time() - t0_decoding) * 1000
		L.warning(
		    ('\n[%s] Latency reformat image (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

"""
Usage example
---------------

# configure input parameters
selector = "/demo/example/**"
type_image = True
tagged_image = True

z_svc = ZenohNativeGet(
	_selector=selector, _session_type="GET",
	type_image=type_image, tagged_image=tagged_image
)
z_svc.init_connection()

z_svc.get()

# closing Zenoh subscription & session
z_svc.close_connection()
"""
