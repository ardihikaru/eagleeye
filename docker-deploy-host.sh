#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
NODES=$1
DELAY=$2
VERSION=$3

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
## check version
if [ -z "$VERSION" ]
then
      echo "\$VERSION is empty"
      VERSION="2.4"  # default value
else
      echo "\$VERSION is NOT empty"
fi

## export display (optional); enable this in case DISPLAY environment has not been set
#export DISPLAY=:0

## add user `root` to the list of authorised access to the X server
xhost local:root

# Deploy Redis
docker run -d \
  -h redis \
  --name redis-service \
  --restart always \
  --network host \
  5g-dive/redis:1.0 /bin/sh -c 'redis-server --appendonly yes'

# Deploy mongo
docker run -d --name mongo-service --network host mongo

# Deploy Web Service
docker run --name ews-service -d \
  --network host \
  -v /home/s010132/devel/eagleeye/web-service/etc/ews.conf:/conf/ews/ews.conf \
  -v /home/s010132/devel/eagleeye/site_conf_files/web-service/site.conf:/conf/ews/site.conf \
  -v /home/s010132/devel/eagleeye/site_conf_files/object-detection-service/site.conf:/conf/dual-det/site.conf \
  "5g-dive/eagleeye/web-service:${VERSION}"

echo "Delaying for $((DELAY + 5)) seconds..."
sleep $((DELAY + 5))

# Deploy Dual-Detection Service
echo "Deploying ${NODES} -Dual-Detection Service- containers..."
for i in $(seq 1 $NODES);
  do
    if [ $i -gt 1 ]
    then
      curl --location --request POST 'http://localhost:8080/api/nodes' \
          --header 'Content-Type: application/json' \
          --data '{
              "candidate_selection": true,
              "persistence_validation": true
          }'
    fi
    
    docker run --runtime=nvidia --name "detection-service-${i}" -d \
      --network host \
      -v /home/s010132/devel/eagleeye/object-detection-service/etc/detection.conf:/conf/dual-det/detection.conf \
      -v /home/s010132/devel/eagleeye/site_conf_files/object-detection-service/site.conf:/conf/dual-det/site.conf \
      -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
      "5g-dive/eagleeye/dual-object-detection-service:${VERSION}";

    echo "Waiting $((DELAY + 3)) seconds for Detection-Service-${i} to be ready..."
    sleep $((DELAY + 3))

done

echo "Delaying for ${DELAY} seconds..."
sleep ${DELAY}

# Deploy Scheduler Service
docker run --name scheduler-service -d \
  --network host \
  -v /home/s010132/devel/eagleeye/scheduler-service/etc/scheduler.conf:/conf/scheduler/scheduler.conf \
  -v /home/s010132/devel/eagleeye/site_conf_files/scheduler-service/site.conf:/conf/scheduler/site.conf \
  -v /home/s010132/devel/eagleeye/data:/app/data \
  "5g-dive/eagleeye/scheduler-service:${VERSION}"

echo "Delaying for ${DELAY} seconds..."
sleep ${DELAY}

# Deploy Visualizer Service
docker run --name visualizer-service -d \
  --network host \
  -v /home/s010132/devel/eagleeye/visualizer-service/etc/visualizer.conf:/conf/visualizer/visualizer.conf \
  -v /home/s010132/devel/eagleeye/site_conf_files/visualizer-service/site.conf:/conf/visualizer/site.conf \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  "5g-dive/eagleeye/visualizer-service:${VERSION}"

echo "Delaying for $((DELAY + 5)) seconds after deploying Visualizer..."
sleep $((DELAY + 3))
