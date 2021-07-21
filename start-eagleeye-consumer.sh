#!/bin/bash

# Capturing input arguments
HOST=$1
PORT=$2
ZENOHHOST=$3

printf "\n>>> FYI: Arg[1]=%s; Arg[2]=%s; Arg[3]=%s \n\n" "HOST" "PORT" "ZENOHHOST"

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

if [ -z "$ZENOHHOST" ]
then
      echo "\$ZENOHPORT is empty"
      ZENOHHOST="tcp/localhost:7446"  # default value
fi

printf "\n>>> Web Service URL is http://%s:%s" ${HOST} ${PORT}
printf "\n>>> Zenoh Host: %s" ${ZENOHHOST}

printf "\n>>> Trying to start consumer . . . \n\n"

curl --location --request POST "http://${HOST}:${PORT}/api/stream/live" \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "algorithm": "YOLOv3",
        "stream": "ZENOH",
        "uri": "'${ZENOHHOST}'",
        "scalable": true,
        "extras": {
            "selector": "/eagle/svc/**"
        }
    }'

printf "\n\n>>> Starting EagleEYE Drone Data Consumer \n\n"