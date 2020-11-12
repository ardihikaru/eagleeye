import socket
import cv2
import numpy
import threading
import time

# TCP_IP = "140.113.68.166"
# TCP_IP = "192.168.43.237"
TCP_IP = "localhost"
# TCP_PORT = 8002
TCP_PORT = 5549
sock = socket.socket()
sock.connect((TCP_IP, TCP_PORT))
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]


class CamThread(threading.Thread):
    def run(self):
        global frame
        global cam
        # path = "/home/ardi/devel/nctu/IBM-Lab/eagleeye/data/5g-dive/videos/june_demo_mission-2.mp4"
        cam = cv2.VideoCapture(0)
        # cam = cv2.VideoCapture(2)
        # cam = cv2.VideoCapture(path)
        while True:
            ret, frame = cam.read()
            print("Frame size:", frame.shape)
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            data = numpy.array(imgencode)
            stringData = data.tostring()
            sock.send( (str(len(stringData)).ljust(16)).encode('utf-8'))
            sock.send( stringData )
            time.sleep(0.033)
            # time.sleep(0.030)

        sock.close()
        cam.release()
        cv2.destroyAllWindows()


cam_t=CamThread()
cam_t.start()



    





