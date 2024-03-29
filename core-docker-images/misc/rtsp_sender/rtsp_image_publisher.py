"""
How to use (Linux):
1. Download EasyDarwin (RTSP Server) here:
    https://github.com/EasyDarwin/EasyDarwin/releases/download/v8.1.0/EasyDarwin-linux-8.1.0-1901141151.tar.gz
2. Extract and go to EasyDarwin directory
3. Start EasyDarwin:
    $ sudo ./start.sh
4. Run this python file:
    $ python sender.py
5. Run FFplay:
    $ ffplay rtsp://localhost/test
"""

import subprocess
import cv2

rtsp_url = "rtsp://localhost/test"

# Setup path of the video file
path = "/home/ardi/devel/nctu/IBM-Lab/eagleeye/data/5g-dive/videos/june_demo_mission-2.mp4"
cap = cv2.VideoCapture(path)

# gather video info to ffmpeg
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

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

# sudo apt-get install h264enc ---> No idea, whether this is required or not!
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("frame read failed")
        break

    # YOUR CODE FOR PROCESSING FRAME HERE

    # write to pipe
    p.stdin.write(frame.tobytes())
