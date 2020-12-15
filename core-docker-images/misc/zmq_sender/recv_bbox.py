import cv2
import imagezmq
import logging
import time

###

L = logging.getLogger(__name__)


###

image_hub = imagezmq.ImageHub(open_port='tcp://localhost:5548', REQ_REP=False)

window_title = "CV Output"
# width = 1080
# height = 720
width = 1920
height = 1080
cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_title, width, height)
while True:  # show received images
    data, encoded_img = image_hub.recv_image()

    # decode image
    t0 = time.time()
    decoded_img = cv2.imdecode(encoded_img, 1)
    t1 = (time.time() - t0) * 1000
    L.warning('\nProc. Latency of Decoding frame: (%.3f ms)' % t1)

    # print(">> data:", data)
    print(">> decoded_img SHAPE:", decoded_img.shape)
    cv2.imshow(window_title, decoded_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
