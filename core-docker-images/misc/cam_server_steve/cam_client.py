import socket
import cv2
import numpy
import threading
import time

# TCP_IP = "140.113.68.166"
TCP_IP = "192.168.43.237"
TCP_PORT = 8002
sock = socket.socket()
sock.connect((TCP_IP, TCP_PORT))
encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), 90]


class CamThread(threading.Thread):
    def run(self):
        global frame
        global cam
        cam = cv2.VideoCapture(0)
        while True:
            ret, frame = cam.read()
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            data = numpy.array(imgencode)
            stringData = data.tostring()
            sock.send( (str(len(stringData)).ljust(16)).encode('utf-8'))
            sock.send( stringData )
            
        sock.close()
        cam.release()
        cv2.destroyAllWindows()


cam_t=CamThread()
cam_t.start()



    





