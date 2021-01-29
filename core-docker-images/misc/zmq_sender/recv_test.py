import cv2
import imagezmq
import logging

###

L = logging.getLogger(__name__)


###

image_hub = imagezmq.ImageHub(open_port='tcp://localhost:4548', REQ_REP=False)

window_title = "CV Test"
width = 1080
height = 720
cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_title, width, height)
while True:  # show received images
    data, image = image_hub.recv_image()
    print(">> data:", data)
    cv2.imshow(window_title, image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
