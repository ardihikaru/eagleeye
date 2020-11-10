import socket
import cv2
import numpy
import time
import datetime
import subprocess



def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


TCP_IP = "10.42.0.98"
# TCP_IP = "localhost"
# TCP_IP = "192.168.1.237"
# TCP_PORT = 8002
TCP_PORT = 5549
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
conn, addr = s.accept()

rtsp_url = "rtsp://localhost/test"

# gather video info to ffmpeg
fps = 20
width = 1920
height = 1080

# command and params for ffmpeg
command = ['ffmpeg',
           '-y',
           '-f', 'rawvideo',
           '-vcodec', 'rawvideo',
           '-pix_fmt', 'bgr24',
           '-s', "{}x{}".format(width, height),
           '-r', str(fps),
           '-i', '-',
           '-c:v', 'libx264',
           '-pix_fmt', 'yuv420p',
           '-preset', 'ultrafast',
           '-f', 'rtsp',
           rtsp_url]

# using subprocess and pipe to fetch frame data
p = subprocess.Popen(command, stdin=subprocess.PIPE)

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

    # write to pipe
    p.stdin.write(decimg.tobytes())

    # print("Frame size:", decimg.shape)
    # cv2.imshow('SERVER', decimg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

s.close()
cv2.destroyAllWindows()

