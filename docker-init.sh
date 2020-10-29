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
      NODES=3  # default value
else
      echo "\$NODES is NOT empty"
fi
## check delay
if [ -z "$DELAY" ]
then
      echo "\$DELAY is empty"
      DELAY=0  # default value
else
      echo "\$DELAY is NOT empty"
fi
## check VERSION
if [ -z "$VERSION" ]
then
      echo "\$VERSION is empty"
      VERSION="2.1"  # default value
else
      echo "\$VERSION is NOT empty"
fi

echo "Cleaning up all available containers: docker-prune-containers.sh"
sh ./docker-prune-containers.sh ${NODES} ${DELAY}

echo "Running image builder script..."
sh ./docker-build-images.sh ${VERSION}

echo "Deploying containers"
sh ./docker-deploy.sh ${DELAY} ${VERSION}

