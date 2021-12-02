import cv2
import imagezmq
import logging
import time

###

L = logging.getLogger(__name__)


###

def decoding_img(encoded_img):
    # decode image
    t0 = time.time()
    _decoded_img = cv2.imdecode(encoded_img, 1)
    t1 = (time.time() - t0) * 1000
    L.warning('Proc. Latency of Decoding frame {}: (%.3f ms) \n'.format(_decoded_img.shape) % t1)

    return _decoded_img


# image_hub = imagezmq.ImageHub(open_port='tcp://192.168.1.10:5548', REQ_REP=False)
image_hub = imagezmq.ImageHub(open_port='tcp://localhost:5548', REQ_REP=False)

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
        decoded_img = decoding_img(img)

        # cv2.imshow(window_title, img)
        cv2.imshow(window_title, decoded_img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    L.warning("Stopped by KeyboardInterrupt")

cv2.destroyAllWindows()
