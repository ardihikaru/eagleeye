"""
   This file provide every common function needed by all Classes of Functions
"""

from datetime import datetime, timedelta
import logging

###

L = logging.getLogger(__name__)


###


def get_current_time():
	return datetime.now().strftime("%H:%M:%S")


def get_imagezmq(zmq_receiver):
	try:
		array_name, image = zmq_receiver.recv_image()
		tmp = array_name.split("-")
		frame_id = int(tmp[0])
		t0 = float(tmp[1])
		return True, frame_id, t0, image

	except Exception as e:
		L.error("[ERROR]: %s" % str(e))
		return False, None, None, None
