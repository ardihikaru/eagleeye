import cv2
import imagezmq
import logging

###

L = logging.getLogger(__name__)


###

# image_hub = imagezmq.ImageHub(open_port='tcp://localhost:5552', REQ_REP=False)
image_hub = imagezmq.ImageHub(open_port='tcp://localhost:5548', REQ_REP=False)

while True:  # show received images
    rpi_name, image = image_hub.recv_image()
    print(">> rpi_name:", rpi_name)
    cv2.imshow(rpi_name, image)  # 1 window for each unique RPi name
    cv2.waitKey(1)
