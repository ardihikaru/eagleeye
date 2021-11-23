import asab
import logging
from ext_lib.utils import letterbox
import numpy as np
import time
from ext_lib.utils import get_current_time
from asab import LOG_NOTICE
from zenoh_lib.functions import scale_image

###

L = logging.getLogger(__name__)


###


class ResizerService(asab.Service):
	"""
		A class to resize images, i.e. from FullHD into padded size (for YOLO)
	"""

	def __init__(self, app, service_name="detection.ResizerService"):
		super().__init__(app, service_name)

		# Special params: from YOLO's config items
		self.img_size = int(asab.Config["objdet:yolo"]["img_size"])
		self.half = bool(int(asab.Config["objdet:yolo"]["half"]))

		self.to_fullhd = asab.Config["image:preprocessing"].getboolean("to_fullhd")
		self.img_width = asab.Config["image:preprocessing"].getint("img_width")
		self.img_height = asab.Config["image:preprocessing"].getint("img_height")

	async def ensure_fullhd_image_input(self, img):
		# perform the image size conversion ONLY when the image is decompressed (decompression=False)
		new_img = img.copy()
		t0_img_resizer = time.time()
		img_height, img_weight, _ = new_img.shape
		if self.to_fullhd and img_height != self.img_height:
			new_img = scale_image(new_img, self.img_height, self.img_width)
		t1_img_resizer = (time.time() - t0_img_resizer) * 1000
		t1_img_resizer = round(t1_img_resizer, 3)

		return new_img, t1_img_resizer

	async def cpu_convert_to_padded_size(self, img):
		L.log(LOG_NOTICE, "#### I am a CPU-based resizer function from ResizerService!")

		# Padded resize
		t0_padded = time.time()
		img4yolo = letterbox(img, new_shape=self.img_size)[0]
		t1_padded = (time.time() - t0_padded) * 1000
		L.log(LOG_NOTICE, ('[{}] Proc. Latency converting into padded size (%.3f ms)'.format(get_current_time()) % t1_padded))
		# TODO: To save the latency to convert FullHD size into padded size	

		# Convert
		t0_convert = time.time()
		img4yolo = img4yolo[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
		img4yolo = np.ascontiguousarray(img4yolo, dtype=np.float16 if self.half else np.float32)  # uint8 to fp16/fp32
		img4yolo /= 255.0  # 0 - 255 to 0.0 - 1.0
		t1_convert = (time.time() - t0_convert) * 1000
		L.log(LOG_NOTICE, '[%s] Proc. Latency converting into yolo format (%.3f ms)' % (get_current_time(), t1_convert))
		# TODO: To save the latency to convert img into yolo format

		return img4yolo, (t1_padded + t1_convert)

	async def gpu_convert_to_padded_size(self, img):
		L.log(LOG_NOTICE, "#### I am a GPU-based resizer function from ResizerService!")

		return img
