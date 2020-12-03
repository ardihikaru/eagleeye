import cv2
import imagezmq
import logging

###

L = logging.getLogger(__name__)


###

image_hub = imagezmq.ImageHub(open_port='tcp://10.194.188.106:32010', REQ_REP=False)

window_title = "EagleEYE Raw"
while True:  # show received images
    data, image = image_hub.recv_image()
    print(">> data:", data)
    cv2.imshow(window_title, image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
