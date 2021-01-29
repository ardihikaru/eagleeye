import cv2
import imagezmq
import logging

###

L = logging.getLogger(__name__)


###

image_hub = imagezmq.ImageHub(open_port='tcp://localhost:5548', REQ_REP=False)

window_title = "CV Output"

# setup window configuration
cv2.namedWindow(window_title, cv2.WND_PROP_FULLSCREEN)
cv2.resizeWindow(window_title, 1280, 720)  # Enter your size

while True:  # show received images
    data, image = image_hub.recv_image()
    print(">> data:", data)
    cv2.imshow(window_title, image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
