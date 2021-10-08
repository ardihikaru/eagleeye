"""with_ImageHub.py -- demonstrate using ImageHub class in with statement
An ImageHub can be instantiated in a "with" statement. This will cause the
ImageHub to be closed after the completion of the with statment block.
1. Run this program in its own terminal window on the mac:
python with_ImageHub.py
This 'receive and display images' program must be running before starting
the RPi image sending program.
2. Run the image sending program on the RPi:
python with_ImageSender.py
A cv2.imshow() window will appear on the Mac showing the tramsmitted images
as a video stream. You can repeat Step 2 and start the with_ImageSender.py
on multiple RPis and each one will cause a new cv2.imshow() window to open.
To end the programs, press Ctrl-C in the terminal window of each program.
"""

import sys
import time
import traceback
import numpy as np
import cv2
from imutils.video import FPS
import imagezmq
import logging
from utils import get_img_fsize_in_float

WINDOW_NAME = "Receiver"

###

L = logging.getLogger(__name__)

###

try:
	L.warning("Start listening.")
	with imagezmq.ImageHub() as image_hub:
		while True:  # receive images until Ctrl-C is pressed

			# rpi_name, image = image_hub.recv_image()
			# print(" >>> image type: {}".format(type(image)))
			# L.warning("Received from: {}; image shape: {}".format(sent_from, image.shape))

			frame_id, jpg_buffer = image_hub.recv_jpg()
			# # print(">>>> jpg_buffer size", type(jpg_buffer))
			# image = cv2.imdecode(np.frombuffer(jpg_buffer, dtype='uint8'), -1)
			# # L.warning("Received from: {}; image shape: {}".format(frame_id, image.shape))
			#
			# img_size, ext = get_img_fsize_in_float(image.nbytes)
			# L.warning("[frame={}] Image Size: {} {}; shape={}".format(frame_id, img_size, ext, image.shape))
			L.warning("[frame={}] received.".format(frame_id))

			# see opencv docs for info on -1 parameter
			# cv2.imshow(WINDOW_NAME, image)  # display images 1 window per sent_from
			# cv2.waitKey(1)
			image_hub.send_reply(b'OK')  # REP reply
except (KeyboardInterrupt, SystemExit):
	pass  # Ctrl-C was pressed to end program; FPS stats computed below
except Exception as ex:
	print('Python error with no Exception handler:')
	print('Traceback error:', ex)
	traceback.print_exc()
finally:
	cv2.destroyAllWindows()  # closes the windows opened by cv2.imshow()
	sys.exit()
