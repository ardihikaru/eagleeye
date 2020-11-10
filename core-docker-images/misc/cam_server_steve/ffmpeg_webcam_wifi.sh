#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
HOST=$1

# Verify input
## check Total worker nodes
if [ -z "$HOST" ]
then
      echo "\$HOST is empty"
      HOST="localhost"  # default value
fi

ffmpeg -f v4l2 -i /dev/video0 -preset ultrafast -vcodec libx264 -tune zerolatency -b 1000k -f mpegts udp://${HOST}:6000

