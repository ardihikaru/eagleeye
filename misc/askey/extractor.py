"""
    Script to extract video streaming / file into frames and send them into another Computer through network
        by using TCP connection

    Creator:
        Muhammad Febrian Ardiansyah (mfardiansyah.eed08g@nctu.edu.tw)
"""
import cv2
import time
import imagezmq
import logging
import argparse
from imutils.video import FileVideoStream
import datetime

###

L = logging.getLogger(__name__)


###

def get_fps(start, num_frames):
    end = datetime.datetime.now()
    elapsed = (end - start).total_seconds()

    return num_frames / elapsed


def default_opencv_reader(option):
    # Setup path of the video file
    if len(option.path) == 1:  # expecting to capture built-in or USB plugged camera
        option.path = int(option.path)
    cap = cv2.VideoCapture(opt.path)
    start = datetime.datetime.now()

    frame_id = 0
    while cap.isOpened():
        frame_id += 1
        t0 = time.time()

        ret, frame = cap.read()
        if not ret:
            print("frame read failed")
            break

        t0_zmq = time.time()
        zmq_id = str(frame_id) + "-" + str(t0_zmq)
        zmq_sender.send_image(zmq_id, frame)
        t1_zmq = (time.time() - t0_zmq) * 1000
        L.warning('Latency [Send imagezmq] of frame-%s: (%.5fms); FPS=(%d)' % (str(frame_id), t1_zmq,
                                                                                get_fps(start, frame_id)))

        time.sleep(opt.zmq_delay)
        # print()


def threaded_opencv_reader(option):
    # Setup path of the video file
    if len(option.path) == 1:  # expecting to capture built-in or USB plugged camera
        option.path = int(option.path)
    cap = FileVideoStream(option.path).start()
    start = datetime.datetime.now()

    frame_id = 0
    while cap.more():
        frame_id += 1
        try:
            t0_zmq = time.time()
            zmq_id = str(frame_id) + "-" + str(t0_zmq)

            frame = cap.read()
            zmq_sender.send_image(zmq_id, frame)

            t1_zmq = (time.time() - t0_zmq) * 1000
            L.warning('Latency [Send imagezmq] of frame-%s: (%.5fms); FPS=(%d)' % (str(frame_id), t1_zmq,
                                                                                   get_fps(start, frame_id)))

            time.sleep(opt.zmq_delay)
        except:
            print("frame read failed")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str,
                        default="/home/ardi/devel/nctu/IBM-Lab/eagleeye/data/5g-dive/videos/june_demo_mission-2.mp4",
                        help='It can be a video file or RTSP/RTMP URL')
    parser.add_argument('--zmq-host', type=str, default="*", help='Server Host IP')
    parser.add_argument('--zmq-port', type=str, default="5550", help='Server Host Port')
    parser.add_argument('--zmq-delay', type=float, default=0.0, help='Delay for sending every frame with ZMQ')
    parser.add_argument('--thread', type=str, default="1", help='Extractor mode for extracting; True (1) or False (0)')

    opt = parser.parse_args()
    print(opt)

    # Setup ZMQ Sender
    zmq_url = 'tcp://{}:{}'.format(opt.zmq_host, opt.zmq_port)
    L.warning("ZMQ URL: %s" % zmq_url)
    zmq_sender = imagezmq.ImageSender(connect_to=zmq_url, REQ_REP=False)

    print("[INFO] starting video file thread...")
    if bool(int(opt.thread)):
        threaded_opencv_reader(opt)
    else:
        default_opencv_reader(opt)
