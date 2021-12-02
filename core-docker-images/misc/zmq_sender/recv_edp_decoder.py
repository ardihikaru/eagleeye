import cv2
import imagezmq
import logging
import time
from zenoh_lib.functions import extract_compressed_tagged_img, scale_image

###

L = logging.getLogger(__name__)


###

# image_hub = imagezmq.ImageHub(open_port='tcp://192.168.1.10:5548', REQ_REP=False)
# image_hub = imagezmq.ImageHub(open_port='tcp://localhost:5548', REQ_REP=False)
image_hub = imagezmq.ImageHub(open_port='tcp://localhost:4444', REQ_REP=False)

window_title = "CV Output"
# width = 1080
# height = 720
width = 1920
height = 1080
cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_title, width, height)

L.warning("Listening to incoming images ...")
try:
    while True:  # show received images
        data, img = image_hub.recv_image()
        L.warning("Captured of decoded image resolution: {}".format(img.shape))

        # decoding image
        img_info, latency_data = extract_compressed_tagged_img(img, is_decompress=False)
        encoded_img = img_info["img"]

        # Testing: try to decode
        decoded_img = cv2.imdecode(encoded_img, 1)  # decompress

        # cv2.imshow(window_title, img)
        cv2.imshow(window_title, decoded_img)

        L.warning("")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    L.warning("Stopped by KeyboardInterrupt")

cv2.destroyAllWindows()
