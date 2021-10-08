import socket
import time
from imutils.video import VideoStream
import imagezmq
import logging
import cv2

###

L = logging.getLogger(__name__)

###

# Accept connections on all tcp addresses, port 5555
# sender = imagezmq.ImageSender(connect_to='tcp://*:5555', REQ_REP=False)
sender = imagezmq.ImageSender(connect_to='tcp://localhost:5555', REQ_REP=False)
rpi_name = socket.gethostname()  # send RPi hostname with each image
L.warning("RPI Name: {}".format(rpi_name))

cap = cv2.VideoCapture(0)

# LIMIT MAX FRAME
MAX_FRAME = 100

# # TARGET CAMERA RESOLUTION
# RESOLUTION_WEIGHT = 1024
# RESOLUTION_HEIGHT = 720
#
# # change the image property
# # use `$ v4l2-ctl --list-formats-ext` to check the available format!
# # install first (if not yet): `$ sudo apt install v4l-utils`
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_WEIGHT)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION_HEIGHT)

try:
    frame_id = 0
    while cap.isOpened():
        try:
            frame_id += 1
            # ret = a boolean return value from getting the frame,
            # frame = the current frame being projected in the video
            ret, frame = cap.read()

            L.warning("[Frame={}] Frame size: {}".format(frame_id, frame.shape))
            sender.send_image(rpi_name, frame)

            # if frame_id == MAX_FRAME:
            #     L.warning("Frame reached out MAX_FRAME(={}). Stop the loop.".format(MAX_FRAME))
            #     exit(0)

        except Exception as e:
            L.error("No more frame to show.")
            break

# when stopped, start saving the CSV files
except KeyboardInterrupt:
    L.warning("[STOPPING] Stopped due to keyboard interruption.")
