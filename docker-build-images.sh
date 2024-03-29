#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
VERSION=$1

# Verify input
## check VERSION
if [ -z "$VERSION" ]
then
      echo "\$VERSION is empty"
      VERSION="2.4"  # default value
else
      echo "\$VERSION is NOT empty"
fi

echo "Building images"
cd redis-service && docker build -t "5g-dive/redis:1.0" .
cd ..
#cd core-docker-images && docker build --no-cache -t "5g-dive/eagleeye/nvidia-gpu-opencv:${VERSION}" .
cd core-docker-images && docker build -t "5g-dive/eagleeye/nvidia-gpu-opencv:${VERSION}" .
cd ..
#cd core-service && docker build --no-cache -t "5g-dive/eagleeye/core-service:${VERSION}" .
cd core-service && docker build -t "5g-dive/eagleeye/core-service:${VERSION}" .
cd ..
#cd web-service && docker build --no-cache -t "5g-dive/eagleeye/web-service:${VERSION}" .
cd web-service && docker build -t "5g-dive/eagleeye/web-service:${VERSION}" .
cd ..
#cd object-detection-service && docker build --no-cache -f Dockerfile-parent -t "5g-dive/eagleeye/dual-object-detection-service-head:${VERSION}" .
cd object-detection-service && docker build -f Dockerfile-parent -t "5g-dive/eagleeye/dual-object-detection-service-head:${VERSION}" .
cd ..
#cd object-detection-service && docker build --no-cache -t "5g-dive/eagleeye/dual-object-detection-service:${VERSION}" .
cd object-detection-service && docker build -t "5g-dive/eagleeye/dual-object-detection-service:${VERSION}" .
cd ..
#cd scheduler-service && docker build --no-cache -t "5g-dive/eagleeye/scheduler-service:${VERSION}" .
cd scheduler-service && docker build -t "5g-dive/eagleeye/scheduler-service:${VERSION}" .
cd ..
#cd visualizer-service && docker build --no-cache -t "5g-dive/eagleeye/visualizer-service:${VERSION}" .
cd visualizer-service && docker build -t "5g-dive/eagleeye/visualizer-service:${VERSION}" .
cd ..
