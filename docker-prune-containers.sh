#!/bin/bash

# Sample:
# bash docker-deploy-network-host.sh 6 2 2
# Deploying 6 detection + 2 drones + with 2 sec delays each

# Capturing expected total number of worker nodes (input arguments)
NODES=$1
DELAY=$2
NUMDRONE=$3

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
## check Total drones
if [ -z "$NUMDRONE" ]
then
      echo "\$NUMDRONE is empty"
      NUMDRONE=3  # default value
else
      echo "\$NUMDRONE is NOT empty (=${NUMDRONE})"
fi

echo "Deleting redis-service..."
docker container rm -f redis-service

echo "Deleting mongo-service..."
docker container rm -f mongo-service

echo "Deleting ews-service..."
docker container rm -f ews-service

echo "Deleting all detection-service; Total=${NODES}..."
for i in $(seq 1 $NODES);
  do docker container rm -f "detection-service-${i}";
done

echo "Deleting pcs-service..."
docker container rm -f pcs-svc

echo "Deleting all pv-service; Total=${NUMDRONE}..."
for i in $(seq 1 $NUMDRONE);
  do docker container rm -f "pv-${i}-svc";
done

echo "Deleting all sorter-service; Total=${NUMDRONE}..."
for i in $(seq 1 $NUMDRONE);
  do docker container rm -f "sorter-${i}-svc";
done

echo "Deleting offloader-service..."
docker container rm -f offloader-service

echo "Deleting all visualizer-service; Total=${NUMDRONE}..."
for i in $(seq 1 $NUMDRONE);
  do
    docker container rm -f "viz-rtsp-ee-svc-${i}";
    docker container rm -f "viz-rtsp-raw-svc-${i}";
done

echo "Deleting eagleeye network..."
docker network rm eagleeye

echo "Delaying for ${DELAY} seconds..."
sleep ${DELAY}