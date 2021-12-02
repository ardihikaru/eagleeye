"""

"""
import cv2
import time
import imagezmq
import logging
from datetime import datetime

###

L = logging.getLogger(__name__)


###

# Encoding parameter
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]  # The default value for IMWRITE_JPEG_QUALITY is 95

# Setup path of the video file
# path = "/home/ardi/devel/nctu/IBM-Lab/eagleeye/data/5g-dive/videos/customTest_MIRC-Roadside-20s.mp4"
# path = "rtsp://140.113.86.98:40000/test"
# path = "rtsp://localhost/test"
path = 0
cap = cv2.VideoCapture(path)

# gather video info to ffmpeg
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Setup ZMQ Sender
# uri = 'tcp://127.0.0.1:5550'
uri = 'tcp://*:5548'
L.warning("ZMQ URI: %s" % uri)
sender = imagezmq.ImageSender(connect_to=uri, REQ_REP=False)


def encode_img(img, _frame_id):
    t0_img_compression = time.time()
    _, compressed_img = cv2.imencode('.jpg', img, encode_param)
    compressed_img_len, _ = compressed_img.shape
    t1_img_compression = (time.time() - t0_img_compression) * 1000
    t1_img_compression = round(t1_img_compression, 3)
    L.warning(('[frame-{}][%s] Latency Image Compression (%.3f ms) \n'.format(_frame_id) % (
        datetime.now().strftime("%H:%M:%S"), t1_img_compression)))

    return compressed_img


frame_id = 0
try:
    while cap.isOpened():
        frame_id += 1
        t0 = time.time()

        ret, frame = cap.read()
        if not ret:
            print("frame read failed")
            break
        L.warning('[Image_Quality] of frame-%s {}'.format(frame.shape))

        # encode frame to reduce the image quality and change its resolution
        encoded_img = encode_img(frame, frame_id)

        t0_zmq = time.time()
        zmq_id = str(frame_id) + "-" + str(t0_zmq)
        # sender.send_image(zmq_id, frame)
        sender.send_image(zmq_id, encoded_img)
        t1_zmq = (time.time() - t0_zmq) * 1000
        L.warning('Latency [Send imagezmq] of frame-%s {}: (%.3fms)'.format(encoded_img.shape) %
                  (str(frame_id), t1_zmq))

        # time.sleep(0.30)
        # print()
except KeyboardInterrupt:
    print("Stopped by KeyboardInterrupt")
