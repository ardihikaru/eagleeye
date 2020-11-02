import socket
import cv2
import numpy


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
TCP_PORT = 8002
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(True)
conn, addr = s.accept()
while 1:
    length = recvall(conn, 16)
    length=length.decode('utf-8')
    stringData = recvall(conn, int(length))
    #stringData = zlib.decompress(stringData)
    #print('old={} new={}'.format(len(stringData), len(zlib.compress(stringData)) ))
    data = numpy.fromstring(stringData, dtype='uint8')
    decimg=cv2.imdecode(data,1)
    decimg = cv2.resize(decimg, (1600, 1200))
    cv2.imshow('SERVER',decimg)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

s.close()
cv2.destroyAllWindows()

