#!/bin/bash

# Capturing Input
# any value can be given.
XHOST=$1

echo "Running shell script file: docker-prune-containers.sh"
sh ./docker-prune-containers.sh 3 2

# Verify input
## check XHOST setup
if [ -z "$XHOST" ]
then
      echo "\$XHOST is empty; add user 'root' to the list of authorised access to the X server"
      ## add user `root` to the list of authorised access to the X server
      xhost local:root
else
      echo "\$XHOST is NOT empty; no need to change the authorization of the X Server"
fi

## Create Docker network
docker network create -d bridge eagleeye

# minor update due to issue: `docker on ubuntu 16.04 error when killing container`
# Source: https://stackoverflow.com/a/49573618
# Deploy Redis
docker run -d \
  -h redis \
  -p 6379:6379 \
  --name redis-service \
  --restart always \
  --network eagleeye \
  --security-opt apparmor=docker-default \
  redis:5.0.5-alpine3.9 /bin/sh -c 'redis-server --appendonly yes'

# minor update due to issue: `docker on ubuntu 16.04 error when killing container`
# Source: https://stackoverflow.com/a/49573618
# Deploy mongo
docker run -d -p 27017:27017 --name mongo-service --network eagleeye mongo --security-opt apparmor=docker-default
