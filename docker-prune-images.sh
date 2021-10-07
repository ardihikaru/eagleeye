#!/bin/bash

# Capturing input arguments
VERSION=$1

# Verify inputs
if [ -z "$VERSION" ]
then
      echo "\$VERSION is empty. Use [2.4] as the default value."
      VERSION="2.4"  # default value
else
      echo "\$VERSION is NOT empty"
fi

docker image rm -f "5g-dive/eagleeye/visualizer-service:${VERSION}"
docker image rm -f "5g-dive/eagleeye/offloader-service:${VERSION}"
docker image rm -f "5g-dive/eagleeye/dual-object-detection-service:${VERSION}"
docker image rm -f "5g-dive/eagleeye/dual-object-detection-service-head:${VERSION}"
docker image rm -f "5g-dive/eagleeye/pv:1.0"
docker image rm -f "5g-dive/eagleeye/pcs:1.0"
docker image rm -f "5g-dive/eagleeye/sorter:1.0"
docker image rm -f "5g-dive/eagleeye/web-service:${VERSION}"
docker image rm -f "5g-dive/eagleeye/pycore-compact:1.0"
docker image rm -f "5g-dive/eagleeye/core-service:${VERSION}"
docker image rm -f "5g-dive/eagleeye/nvidia-gpu-opencv:${VERSION}"
docker image rm -f "5g-dive/eagleeye/cuda-cv-ffmpeg-py38:1.0"

# Try to remove all dangling images (if any)
if [ -z $(docker images --filter "dangling=true" -q --no-trunc) ]
then
	echo "Trying to remove dangling images, but there is None. NOTHING TO DO HERE. :)"
else
	echo "Dangling images have been pruned successfully. :)"
	docker rmi -f $(docker images --filter "dangling=true" -q --no-trunc)
fi
