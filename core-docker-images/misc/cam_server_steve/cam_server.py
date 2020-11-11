import socket
import cv2
import numpy
import time
import datetime


def get_fps(start, num_frames):
    end = datetime.datetime.now()
    elapsed = (end - start).total_seconds()
    print(" >>> elapsed:", elapsed)

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
TCP_IP = "localhost"
# TCP_IP = "192.168.1.237"
# TCP_PORT = 8002
TCP_PORT = 5550
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
conn, addr = s.accept()

# start = None
num_frames = 0
start_time=time.time()
print(">>> MULAI ..")
while 1:
    num_frames+=1
    now_time=time.time()
    used_time=now_time-start_time
    if used_time >= 2:
        fps=num_frames/used_time
        num_frames=0
        start_time=time.time()
        print('FPS=(%.2f)' % fps)

    # num_frames += 1

    length = recvall(conn, 16)
    length=length.decode('utf-8')
    t0_recv = time.time()
    stringData = recvall(conn, int(length))
    # if start is None:
    #     start = datetime.datetime.now()
    t1_recv = time.time() - t0_recv
    print('\nLatency RECV frame: (%.2f ms)' % (t1_recv * 1000))
    #stringData = zlib.decompress(stringData)
    #print('old={} new={}'.format(len(stringData), len(zlib.compress(stringData)) ))
    t1 = time.time()
    data = numpy.fromstring(stringData, dtype='uint8')
    decimg=cv2.imdecode(data, 1)
    t2 = time.time() - t1
    print('\nLatency Convert: (%.2f ms)' % (t2 * 1000))

    # recv_time = datetime.datetime.now()
    # print('num_frames=%d; FPS=(%d)' % (num_frames, get_fps(start, num_frames)))

    # decimg = cv2.resize(decimg, (1600, 1200))
    decimg = cv2.resize(decimg, (1920, 1080))
    print("Frame size:", decimg.shape)
    cv2.imshow('SERVER', decimg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

s.close()
cv2.destroyAllWindows()

