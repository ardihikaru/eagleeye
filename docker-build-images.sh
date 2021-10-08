#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
VERSION=$1

# Sample:
# bash docker-build-images.sh
# Deploying with using version "2.4" (default)

# Verify input
## check VERSION
if [ -z "$VERSION" ]
then
      echo "\$VERSION is empty"
      VERSION="2.4"  # default value
else
      echo "\$VERSION is NOT empty"
fi

echo "Building images . . ."

echo "1. Pull redis image [redis:5.0.5-alpine3.9]"
docker pull redis:5.0.5-alpine3.9

echo "2. Building PARENT GPU-based image (it will be used by most of the images)"
cd core-docker-images && docker build -f Dockerfile-parent -t "5g-dive/eagleeye/cuda-cv-ffmpeg-py38:1.0" .
cd ..

echo "3. Building CHILD GPU-based image (it will be used by most of the images)"
cd core-docker-images && docker build -t "5g-dive/eagleeye/nvidia-gpu-opencv:${VERSION}" .
cd ..

echo "4. Building GPU-Enabled Pycore image"
#cd core-service && docker build --no-cache -t "5g-dive/eagleeye/core-service:${VERSION}" .
cd core-service && docker build -t "5g-dive/eagleeye/core-service:${VERSION}" .
cd ..

echo "5. Building Non-GPU Pycore image"
#cd core-service && docker build --no-cache -t "5g-dive/eagleeye/core-service:${VERSION}" .
cd core-service && docker build -f Dockerfile-compact -t "5g-dive/eagleeye/pycore-compact:1.0" .
cd ..

echo "6. Building Web Service image"
#cd web-service && docker build --no-cache -t "5g-dive/eagleeye/web-service:${VERSION}" .
cd web-service && docker build -t "5g-dive/eagleeye/web-service:${VERSION}" .
cd ..

echo "7. Building Sorter image"
#cd sorter_service && docker build --no-cache -t "5g-dive/eagleeye/sorter:1.0" .
cd sorter_service && docker build -t "5g-dive/eagleeye/sorter:1.0" .
cd ..

echo "8. Building PiH Candidate Selection (PCS) image"
#cd pih-candidate-selection-service && docker build --no-cache -t "5g-dive/eagleeye/pcs:1.0" .
cd pih-candidate-selection-service && docker build -t "5g-dive/eagleeye/pcs:1.0" .
cd ..

echo "9. Building PiH Validation (PV) image"
#cd pih-persistance-validation-service && docker build --no-cache -t "5g-dive/eagleeye/pv:1.0" .
cd pih-persistance-validation-service && docker build -t "5g-dive/eagleeye/pv:1.0" .
cd ..

echo "10. Building Object Detection BASE image"
#cd object-detection-service && docker build --no-cache -f Dockerfile-parent -t "5g-dive/eagleeye/dual-object-detection-service-head:${VERSION}" .
cd object-detection-service && docker build -f Dockerfile-parent -t "5g-dive/eagleeye/dual-object-detection-service-head:${VERSION}" .
cd ..

echo "11. Building Object Detection CHILD image"
#cd object-detection-service && docker build --no-cache -t "5g-dive/eagleeye/dual-object-detection-service:${VERSION}" .
cd object-detection-service && docker build -t "5g-dive/eagleeye/dual-object-detection-service:${VERSION}" .
cd ..

echo "12. Building Offloader image"
#cd data_offloader_service && docker build --no-cache -t "5g-dive/eagleeye/offloader-service:${VERSION}" .
cd data_offloader_service && docker build -t "5g-dive/eagleeye/offloader-service:${VERSION}" .
cd ..

echo "13. Building Visualizer image"
#cd visualizer-service && docker build --no-cache -t "5g-dive/eagleeye/visualizer-service:${VERSION}" .
cd visualizer-service && docker build -t "5g-dive/eagleeye/visualizer-service:${VERSION}" .
cd ..

echo "All images have been successfully built."
echo "Please continue with the deployment process. Enjoy! :)"
