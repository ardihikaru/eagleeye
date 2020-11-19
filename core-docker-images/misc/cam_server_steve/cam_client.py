import socket
import cv2
import numpy
import threading
import time

# TCP_IP = "140.113.68.166"
# TCP_IP = "192.168.43.237"
TCP_IP = "localhost"
# TCP_IP = "10.194.188.250"
# TCP_PORT = 8002
TCP_PORT = 5549
sock = socket.socket()
sock.connect((TCP_IP, TCP_PORT))
# encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
_num_skipped_frames = 0


class CamThread(threading.Thread):
    def run(self):
        global frame
        global cam
        # path = "/home/ardi/devel/nctu/IBM-Lab/eagleeye/data/5g-dive/videos/june_demo_mission-2.mp4"
        cam = cv2.VideoCapture(0)
        # cam = cv2.VideoCapture(2)
        # cam = cv2.VideoCapture(path)

        # variables used to skip some frames
        received_frame_id = 0
        skip_count = -1

        while True:
            received_frame_id += 1
            skip_count += 1

            # try skipping frames
            if _num_skipped_frames > 0 and received_frame_id > 1 and skip_count <= _num_skipped_frames:
                # skip this frame
                print(">>> Skipping frame-{}; Current `skip_count={}`".format(str(received_frame_id), str(skip_count)))
            else:
                ret, frame = cam.read()
                print("Frame size:", frame.shape)
                result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                data = numpy.array(imgencode)
                stringData = data.tostring()
                sock.send((str(len(stringData)).ljust(16)).encode('utf-8'))
                sock.send(stringData)
                time.sleep(0.033)
                # time.sleep(0.030)

            # reset skipping frames
            if 0 < _num_skipped_frames < skip_count:
                skip_count = 0

        sock.close()
        cam.release()
        cv2.destroyAllWindows()


cam_t=CamThread()
cam_t.start()



    





