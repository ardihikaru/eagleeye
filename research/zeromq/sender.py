import socket
import time
from imutils.video import VideoStream
import imagezmq
import cv2

# Accept connections on all tcp addresses, port 5555
sender = imagezmq.ImageSender(connect_to='tcp://*:5555', REQ_REP=False)
rpi_name = socket.gethostname() # send RPi hostname with each image
print(">> rpi_name:", rpi_name)

time.sleep(2.0)  # allow camera sensor to warm up
img_path = "./data/5g-dive/sample-1-frame/out8.png"
image = cv2.imread(img_path, 0)
while True:  # read an image and keep sending the same image
    sender.send_image(rpi_name, image)
