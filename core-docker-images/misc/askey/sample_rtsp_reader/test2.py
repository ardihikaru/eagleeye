import cv2
import socket


# # TCP_IP = "140.113.68.166"
# # TCP_IP = "192.168.43.237"
# TCP_IP = "localhost"
# # TCP_PORT = 8002
# TCP_PORT = 5549
# sock = socket.socket()
# sock.connect((TCP_IP, TCP_PORT))
# encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]


# path = 0
path = 2
cap = cv2.VideoCapture(path)
while True:
    ret, frame = cap.read()
    if ret == True:
        print(">>>> load frame:", frame.shape)
        cv2.imshow('frame_2', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        else:
            pass
