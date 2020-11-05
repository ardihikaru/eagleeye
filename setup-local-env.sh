#!/bin/bash

echo "Running shell script file: docker-prune-containers.sh"
sh ./docker-prune-containers.sh 3 2

## add user `root` to the list of authorised access to the X server
xhost local:root

## Create Docker network
docker network create -d bridge eagleeye

# Deploy Redis
docker run -d \
  -h redis \
  -p 6379:6379 \
  --name redis-service \
  --restart always \
  --network eagleeye \
  5g-dive/redis:1.0 /bin/sh -c 'redis-server --appendonly yes'

# Deploy mongo
docker run -d -p 27017:27017 --name mongo-service --network eagleeye mongo
