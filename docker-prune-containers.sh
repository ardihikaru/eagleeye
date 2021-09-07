#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
NODES=$1
DELAY=$2

# Verify input
## check Total worker nodes
if [ -z "$NODES" ]
then
      echo "\$NODES is empty"
      NODES=2  # default value
else
      echo "\$NODES is NOT empty"
fi
## check delay
if [ -z "$DELAY" ]
then
      echo "\$DELAY is empty"
      DELAY=2  # default value
else
      echo "\$DELAY is NOT empty"
fi

echo "Deleting redis-service..."
docker container rm -f redis-service

echo "Deleting mongo-service..."
docker container rm -f mongo-service

echo "Deleting ews-service..."
docker container rm -f ews-service

echo "Deleting all detection-service; Total=$1..."
for i in $(seq 1 $NODES);
  do docker container rm -f "detection-service-${i}";
done

echo "Deleting all pv-service; Total=$1..."
for i in $(seq 1 $NODES);
  do docker container rm -f "pv-${i}-svc";
done

echo "Deleting all sorter-service; Total=$1..."
for i in $(seq 1 $NODES);
  do docker container rm -f "sorter-${i}-svc";
done

echo "Deleting pcs-service..."
docker container rm -f pcs-svc

echo "Deleting offloader-service..."
docker container rm -f offloader-service

echo "Deleting visualizer-service..."
docker container rm -f visualizer-service

echo "Deleting eagleeye network..."
docker network rm eagleeye

echo "Delaying for ${DELAY} seconds..."
sleep ${DELAY}