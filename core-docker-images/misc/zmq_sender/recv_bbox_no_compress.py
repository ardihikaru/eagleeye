import cv2
import imagezmq
import logging
import time

###

L = logging.getLogger(__name__)


###

# image_hub = imagezmq.ImageHub(open_port='tcp://192.168.1.10:5548', REQ_REP=False)
image_hub = imagezmq.ImageHub(open_port='tcp://localhost:5548', REQ_REP=False)

window_title = "CV Output"
# width = 1080
# height = 720
width = 1920
height = 1080
cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_title, width, height)
while True:  # show received images
    data, img = image_hub.recv_image()

    # print(">> data:", data)
    print(">> img SHAPE:", img.shape)
    cv2.imshow(window_title, img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
