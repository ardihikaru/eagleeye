#!/bin/bash

ffmpeg -re -i /home/s010132/devel/eagleeye/data/5g-dive/videos/customTest_MIRC-Roadside-20s.mp4 -rtsp_transport tcp -vcodec h264 -f rtsp rtsp://140.113.86.92/input
