#!/bin/bash

# Sample:
# bash docker-deploy-network-host.sh 6 2 2 "OK"
# Deploying 6 detection + 2 drones + with 2 sec delays + To enable/disable XHOST

# Capturing Input
# any value can be given.
NODES=$1
DELAY=$2
NUMDRONE=$3
XHOST=$4

# Verify input
## check Total worker nodes
if [ -z "$NODES" ]
then
      echo "\$NODES is empty"
      NODES=2  # default value
else
      echo "\$NODES is NOT empty (=${NODES})"
fi

## check delay
if [ -z "$DELAY" ]
then
      echo "\$DELAY is empty"
      DELAY=2  # default value
else
      echo "\$DELAY is NOT empty (=${DELAY})"
fi

## check number of connected drones
if [ -z "$NUMDRONE" ]
then
      echo "\$$NUMDRONE is empty"
      NUMDRONE=1  # default value
else
      echo "\$$NUMDRONE is NOT empty (=${NUMDRONE})"
fi

echo "Running shell script file: docker-prune-containers.sh"
sh ./docker-prune-containers.sh ${NODES} ${DELAY} ${NUMDRONE}

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
docker run -d -p 27017:27017 --name mongo-service --network eagleeye --security-opt apparmor=docker-default mongo
