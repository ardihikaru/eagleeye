#!/bin/bash

# Sample:
# bash docker-deploy-network-host.sh 6 2 2 "192.168.1.60"
# Deploying 6 detection + 2 drones + with 2 sec delays each + consumer in IP=192.168.1.60

# Capturing expected total number of worker nodes (input arguments)
NODES=$1
DELAY=$2
NUMDRONE=$3
CONSUMERIP=$4
VERSION=$5

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

## check consumer port (in offloader service)
if [ -z "$CONSUMERIP" ]
then
      echo "\$CONSUMERIP is empty"
      CONSUMERIP="localhost"  # default value
else
      echo "\$CONSUMERIP is NOT empty (=${CONSUMERIP})"
fi

## check version
if [ -z "$VERSION" ]
then
      echo "\$VERSION is empty"
      VERSION="2.4"  # default value
else
      echo "\$VERSION is NOT empty (=${VERSION})"
fi

## add user `root` to the list of authorised access to the X server
xhost local:root

bash ./setup-local-env.sh ${NODES} ${DELAY} ${NUMDRONE}

# Deploy Web Service
docker run --name ews-service -d \
          --network host \
          -v /home/s010132/devel/eagleeye/web-service/etc/site-docker.conf:/app/etc/site.conf \
          -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
          "5g-dive/eagleeye/web-service:${VERSION}";

echo "Delaying for $((DELAY + 5)) seconds..."
sleep $((DELAY + 5))

# Deploy Sorter Services
echo "Deploying Sorter Services ..."
for i in $(seq 1 $NUMDRONE);
  do
    docker run --name "sorter-${i}-svc" -d --network host \
    -v "/home/s010132/devel/eagleeye/sorter_service/etc/site-${i}.conf:/app/etc/site.conf" \
    5g-dive/eagleeye/sorter:1.0;

    echo "[sorter-${i}-svc] is deployed ..."
done

# Deploy PiH PCS Service
echo "Deploying [pcs-svc] ..."
docker run --name pcs-svc --network host -d \
-v /home/s010132/devel/eagleeye/pih-candidate-selection-service/etc/site.conf:/app/etc/site.conf \
5g-dive/eagleeye/pcs:1.0
echo "[pcs-svc] is deployed ..."

# Deploy PiH PV Services
echo "Deploying PiH PV Services ..."
for i in $(seq 1 $NUMDRONE);
  do
    docker run --name "pv-${i}-svc" --network host -d \
    -v "/home/s010132/devel/eagleeye/pih-persistance-validation-service/etc/site-${i}.conf:/app/etc/site.conf" \
    5g-dive/eagleeye/pv:1.0

    echo "[pv-${i}-svc] is deployed ..."
done

# Deploy Detection Service
echo "Deploying ${NODES} -Detection Service- containers..."
for i in $(seq 1 $NODES);
  do
    if [ $i -gt 1 ]
    then
      curl --location --request POST 'http://localhost:8079/api/nodes' \
          --header 'Content-Type: application/json' \
          --data '{
              "candidate_selection": true,
              "persistence_validation": true
          }'
    fi

    docker run --runtime=nvidia --name "detection-service-${i}" -d \
              --network host \
              -v /home/s010132/devel/eagleeye/object-detection-service/etc/site-docker.conf:/app/etc/site.conf \
              -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
              "5g-dive/eagleeye/dual-object-detection-service:${VERSION}";
    echo "[detection-service-${i}] is deployed ..."

    echo "Waiting $((DELAY + 3)) seconds for Detection-Service-${i} to be ready..."
    sleep $((DELAY + 3))

done

echo "Delaying for ${DELAY} seconds..."
sleep ${DELAY}

# Deploy Offloader Service
docker run --name offloader-service -d \
          --network host \
          -v /home/s010132/devel/eagleeye/data_offloader_service/etc/site-docker.conf:/app/etc/site.conf \
          "5g-dive/eagleeye/offloader-service:${VERSION}"

echo "Delaying for ${DELAY} seconds..."
sleep ${DELAY}

# Deploy Visualizer Services
echo "Deploying Visualizer Services ..."
for i in $(seq 1 $NUMDRONE);
  do
    docker run --name "viz-rtsp-ee-svc-${i}" -d \
                  --network host \
                  -v "/home/s010132/devel/eagleeye/visualizer-service/etc/site-rtsp-${i}.conf:/app/etc/site.conf" \
                  "5g-dive/eagleeye/visualizer-service:${VERSION}"
    echo "[viz-rtsp-ee-svc-${i}] is deployed ..."

    docker run --name "viz-rtsp-raw-svc-${i}" -d \
                  --network host \
                  -v "/home/s010132/devel/eagleeye/visualizer-service/etc/site-rtsp-raw-${i}.conf:/app/etc/site.conf" \
                  "5g-dive/eagleeye/visualizer-service:${VERSION}"
    echo "[viz-rtsp-raw-svc-${i}] is deployed ..."

done

echo "Delaying for $((DELAY + 5)) seconds after deploying Visualizer..."
sleep $((DELAY + 3))

echo "Activating consumer with IP=${CONSUMERIP} ..."
curl --location --request POST "http://localhost:8079/api/stream/live" \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "algorithm": "YOLOv3",
            "stream": "ZENOH",
            "uri": "tcp/'${CONSUMERIP}':7446",
            "scalable": true,
            "extras": {
                "selector": "/eagle/svc/**"
            }
        }'

echo ""
echo "Auto deployment script done. Enjoy! :)"
