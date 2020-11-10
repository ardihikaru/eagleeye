import socket
import cv2
import numpy
import imagezmq
import time
import datetime


def get_fps(start, num_frames):
    end = datetime.datetime.now()
    elapsed = (end - start).total_seconds()

    return num_frames / elapsed


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# TCP_IP = "10.42.0.98"
# TCP_IP = "localhost"
TCP_IP = "192.168.1.237"
# TCP_PORT = 8002
# TCP_PORT = 5549
TCP_PORT = 5548
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
conn, addr = s.accept()

# Setup ZMQ Sender
zmq_host = "*"
zmq_port = "5549"
zmq_url = 'tcp://{}:{}'.format(zmq_host, zmq_port)
print("ZMQ URL: %s" % zmq_url)
zmq_sender = imagezmq.ImageSender(connect_to=zmq_url, REQ_REP=False)

start = datetime.datetime.now()
frame_id = 0
while True:
    frame_id += 1
    
    length = recvall(conn, 16)
    length=length.decode('utf-8')
    stringData = recvall(conn, int(length))
    #stringData = zlib.decompress(stringData)
    #print('old={} new={}'.format(len(stringData), len(zlib.compress(stringData)) ))
    data = numpy.fromstring(stringData, dtype='uint8')
    frame = cv2.imdecode(data, 1)
    # frame = cv2.resize(frame, (1600, 1200))
    frame = cv2.resize(frame, (1920, 1080))
    print("Frame size:", frame.shape)

    try:
        t0_zmq = time.time()
        zmq_id = str(frame_id) + "-" + str(t0_zmq)

        # frame = cap.read()
        zmq_sender.send_image(zmq_id, frame)

        t1_zmq = (time.time() - t0_zmq) * 1000
        print('Latency [Send imagezmq] of frame-%s: (%.5fms); FPS=(%d)' % (str(frame_id), t1_zmq,
                                                                               get_fps(start, frame_id)))

        # time.sleep(opt.zmq_delay)
    except:
        print("frame read failed")
        break
    
    # cv2.imshow('SERVER',frame)
    # if cv2.waitKey(30) & 0xFF == ord('q'):
    #     break

s.close()
# cv2.destroyAllWindows()

