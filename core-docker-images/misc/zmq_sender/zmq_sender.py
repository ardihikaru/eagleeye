"""

"""
import cv2
import time
import imagezmq
import logging

###

L = logging.getLogger(__name__)


###

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

frame_id = 0
while cap.isOpened():
    frame_id += 1
    t0 = time.time()

    ret, frame = cap.read()
    if not ret:
        print("frame read failed")
        break

    print(">>> Sending frames-%s" % str(frame_id))
    t0_zmq = time.time()
    zmq_id = str(frame_id) + "-" + str(t0_zmq)
    sender.send_image(zmq_id, frame)
    t1_zmq = (time.time() - t0_zmq) * 1000
    L.warning('Latency [Send imagezmq] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
    #
    # time.sleep(0.30)
    # print()
