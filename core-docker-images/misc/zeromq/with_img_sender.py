"""with_ImageSender.py -- demonstrate using ImageSender class in with statement.
A Raspberry Pi test program that uses imagezmq to send image frames from the
PiCamera continuously to a receiving program on a Mac that will display the
images as a video stream. Images are jpg compressed before sending.
This program requires that the image receiving program be running first. Brief
test instructions are in that program: with_ImageHub.py.
"""

import sys
import socket
import time
import traceback
import cv2
import imagezmq
import logging
from utils import get_img_fsize_in_float

###

L = logging.getLogger(__name__)

# TARGET CAMERA RESOLUTION
RESOLUTION_WEIGHT = 1920
RESOLUTION_HEIGHT = 1080

###

# use either of these formats to specifiy address of display computer
#     with imagezmq.ImageSender(connect_to='tcp://jeff-macbook:5555')
#     with imagezmq.ImageSender(connect_to='tcp://192.168.1.190:5555')
# change the line below: with imagezmq.ImageSender()... as needed

rpi_name = socket.gethostname()  # send RPi hostname with each image

# picam = VideoStream(usePiCamera=True).start()
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("/home/ardi/Desktop/samsung-sample-fhd.webm")

# # change the image property
# # use `$ v4l2-ctl --list-formats-ext` to check the available format!
# # install first (if not yet): `$ sudo apt install v4l-utils`
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_WEIGHT)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION_HEIGHT)

time.sleep(2.0)  # allow camera sensor to warm up
jpeg_quality = 95  # 0 to 100, higher is better quality, 95 is cv2 default

try:
	# with imagezmq.ImageSender(connect_to='tcp://192.168.86.34:5555') as sender:
	with imagezmq.ImageSender(connect_to='tcp://localhost:5555') as sender:
		frame_id = 0
		while cap.isOpened():
			frame_id += 1
			ret, frame = cap.read()

			img_size, ext = get_img_fsize_in_float(frame.nbytes)

			ret_code, jpg_buffer = cv2.imencode(
				".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
			buf_img_size, buf_ext = get_img_fsize_in_float(jpg_buffer.nbytes)
			buf_img_size = round(buf_img_size, 2)

			L.warning("[Frame={}] Frame size: {}; Image Size: (Original={} {}). (Compress={} {})".format(
				frame_id, frame.shape,
				img_size, ext,
				buf_img_size, buf_ext,
			))
			reply_from_mac = sender.send_jpg(frame_id, jpg_buffer)

			# above line shows how to capture REP reply text from Mac
except (KeyboardInterrupt, SystemExit):
	pass  # Ctrl-C was pressed to end program
except Exception as ex:
	print('Python error with no Exception handler:')
	print('Traceback error:', ex)
	traceback.print_exc()
finally:
	sys.exit()
