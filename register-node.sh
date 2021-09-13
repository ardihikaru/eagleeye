#!/bin/bash

# Capturing input arguments
HOST=$1
PORT=$2

printf "\n>>> FYI: Arg[1]=%s; Arg[2]=%s \n\n" "HOST" "PORT"

if [ -z "$HOST" ]
then
      echo "\$HOST is empty"
      HOST="localhost"  # default value
fi

if [ -z "$PORT" ]
then
      echo "\$PORT is empty"
      PORT="8079"  # default value
fi

printf "\n>>> Web Service URL is http://%s:%s" ${HOST} ${PORT}
printf "\n>>> API to register new node URL is http://%s:%s/api/nodes \n\n" ${HOST} ${PORT}

printf "\n>>> Trying to register a new node . . . \n\n"

curl --location --request POST "http://${HOST}:${PORT}/api/nodes" \
    --header 'Content-Type: application/json' \
    --data '{
        "candidate_selection": true,
        "persistence_validation": true
    }'

printf "\n\n>>> Registering a new node succeed\n\n"