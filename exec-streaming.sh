#!/bin/bash

# Sample run:
# Native:
## $ . exec-streaming.sh /home/s010132/devel/eagleeye/data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4
# Docker:
## $ . exec-streaming.sh /app/data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4
## $ . exec-streaming.sh udp://localhost:6000

# Capturing input arguments
FPATH=$1
HOST=$2
PORT=$3
MODE=$4

printf "\n>>> FYI: Arg[1]=%s; Arg[2]=%s; Arg[3]=%s; Arg[4]=%s \n\n" \
  "FPATH (default=/home/s010132/devel/eagleeye/data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4)" \
  "HOST (default=localhost)" \
  "PORT (default=8080)" \
  "MODE (default=STREAM)"

if [ -z "$HOST" ]
then
      echo "\$HOST is empty"
      HOST="localhost"  # default value
fi

if [ -z "$PORT" ]
then
      echo "\$PORT is empty"
      PORT="8080"  # default value
fi

if [ -z "$FPATH" ]
then
      echo "\$FPATH is empty"
      FPATH="/home/s010132/devel/eagleeye/data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4"  # default value
fi

if [ -z "$MODE" ]
then
      echo "\$MODE is empty"
      MODE="STREAM"  # default value
fi

printf "\n>>> Web Service URL is [http://%s:%s]" ${HOST} ${PORT}
printf "\n>>> API to start capturing streaming URL is [http://%s:%s/api/stream/live]" ${HOST} ${PORT}
printf "\n>>> VIDEO FILE PATH is [%s]" ${FPATH}
printf "\n>>> Capturing Mode is [%s]\n\n" ${MODE}


curl --location --request POST "http://${HOST}:${PORT}/api/stream/live" \
    --header "Content-Type: application/json" \
    --data "{
        \"algorithm\": \"YOLOv3\",
        \"stream\": \"${MODE}\",
        \"uri\": \"${FPATH}\",
        \"scalable\": true
    }"

printf "\n\n>>> EagleEYE started to capture and detect PiH objects\n\n"
