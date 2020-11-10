#!/bin/bash

# Capturing input arguments
VERSION=$1

# Verify inputs
if [ -z "$VERSION" ]
then
      echo "\$VERSION is empty"
      VERSION="2.3"  # default value
else
      echo "\$VERSION is NOT empty"
fi

docker image rm -f "5g-dive/eagleeye/visualizer-service:${VERSION}"
docker image rm -f "5g-dive/eagleeye/dual-object-detection-service:${VERSION}"
docker image rm -f "5g-dive/eagleeye/scheduler-service:${VERSION}"
docker image rm -f "5g-dive/eagleeye/dual-object-detection-service-head:${VERSION}"
docker image rm -f "5g-dive/eagleeye/web-service:${VERSION}"
docker image rm -f "5g-dive/eagleeye/nvidia-gpu-opencv:${VERSION}"
