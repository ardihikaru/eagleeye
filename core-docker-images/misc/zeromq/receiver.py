import cv2
import imagezmq
import logging

###

L = logging.getLogger(__name__)

###

# set hostname
# hostname = "localhost"
hostname = "ardi-tuf"
# hostname = "scheduler"

# Instantiate and provide the first publisher address
image_hub = imagezmq.ImageHub(open_port='tcp://%s:5555' % hostname, REQ_REP=False)

L.warning("Start listening.")
while True:  # show received images
	rpi_name, image = image_hub.recv_image()
	print(" >>> image type: {}".format(type(image)))
	L.warning("Received from: {}; image shape: {}".format(sent_from, image.shape))

	cv2.imshow(rpi_name, image)  # 1 window for each unique RPi name
	cv2.waitKey(1)

	image_hub.send_reply(b'OK')  # REP reply

