import cv2
import imagezmq

# set hostname
hostname = "localhost"
# hostname = "scheduler"

# Instantiate and provide the first publisher address
image_hub = imagezmq.ImageHub(open_port='tcp://%s:5555' % hostname, REQ_REP=False)

while True:  # show received images
    rpi_name, image = image_hub.recv_image()
    cv2.imshow(rpi_name, image)  # 1 window for each unique RPi name
    cv2.waitKey(1)
