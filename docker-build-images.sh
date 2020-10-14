#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
VERSION=$1

# Verify input
## check VERSION
if [ -z "$VERSION" ]
then
      echo "\$VERSION is empty"
      VERSION="1.0"  # default value
else
      echo "\$VERSION is NOT empty"
fi

echo "Building images"
cd core-docker-images && docker build --no-cache -t "5g-dive/eagleeye/nvidia-gpu-opencv:${VERSION}" . && cd ..
cd web-service && docker build --no-cache -t "5g-dive/eagleeye/web-service:${VERSION}" . && cd ..
cd object-detection-service && docker build --no-cache -f Dockerfile-parent -t "5g-dive/eagleeye/dual-object-detection-service-head:${VERSION}" . && cd ..
cd object-detection-service && docker build --no-cache -t "5g-dive/eagleeye/dual-object-detection-service:${VERSION}" . && cd ..
cd scheduler-service && docker build --no-cache -t "5g-dive/eagleeye/scheduler-service:${VERSION}" . && cd ..
cd visualizer-service && docker build --no-cache -t "5g-dive/eagleeye/visualizer-service:${VERSION}" . && cd ..

echo "Deploying containers"
sh ./docker-deploy.sh

