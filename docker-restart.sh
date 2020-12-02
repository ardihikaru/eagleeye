#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
NODES=$1
DEPLOY_MODE=$2
DELAY=$3
VERSION=$4

# Verify input
## check Total worker nodes
if [ -z "$NODES" ]
then
      echo "\$NODES is empty"
      NODES=2  # default value
else
      echo "\$NODES is NOT empty"
fi
## check Deployment mode: "NETWORK" (default) or "HOST"
if [ -z "$DEPLOY_MODE" ]
then
      echo "\$DEPLOY_MODE is empty"
      DEPLOY_MODE="NETWORK"  # default value
else
      echo "\$DEPLOY_MODE is NOT empty"
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

echo "Running shell script file: docker-prune-containers.sh"
sh ./docker-prune-containers.sh ${NODES} ${DELAY}

echo "Running shell script file: docker-deploy.sh or docker-deploy-host.sh"
if [ "$DEPLOY_MODE" = "HOST" ]; then
    echo "Deploying with the same network as the Host (localhost)."
    sh ./docker-deploy-host.sh ${NODES} ${DELAY} ${VERSION}
else
    echo "Deploying with network 'eagleeye'."
    sh ./docker-deploy.sh ${NODES} ${DELAY} ${VERSION}
fi