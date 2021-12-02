#!/bin/bash

# Note: If the docker unable to connect into the internet (i.e. cannot perform `apt get update`),
# do this: $ systemctl restart docker

# Capturing expected total number of worker nodes (input arguments)
NODES=$1
DEPLOY_MODE=$2
DELAY=$3
VERSION=$4

# Verify input
## check Total worker nodes
# TODO: Update this scripts!
if [ -z "$NODES" ]
then
      NODES=2  # default value
      echo "\$NODES is empty; Set value as ${NODES}"
else
      echo "\$NODES (=${NODES}) is NOT empty"
fi
## check Deployment mode: "NETWORK" (default) or "HOST"
if [ -z "$DEPLOY_MODE" ]
then
      DEPLOY_MODE="HOST"  # default value
      echo "\$DEPLOY_MODE is empty; Set value as ${DEPLOY_MODE}"
else
      echo "\$DEPLOY_MODE (=${DEPLOY_MODE}) is NOT empty"
fi
## check delay
if [ -z "$DELAY" ]
then
      DELAY=0  # default value
      echo "\$DELAY is empty; Set value as ${DELAY}"
else
      echo "\$DELAY (=${DELAY}) is NOT empty"
fi
## check VERSION
if [ -z "$VERSION" ]
then
      VERSION="2.4"  # default value
      echo "\$VERSION is empty; Set value as ${VERSION}"
else
      echo "\$VERSION (=${VERSION}) is NOT empty"
fi

# TODO: Update this scripts!
echo "Cleaning up all available containers: docker-prune-containers.sh"
sh ./docker-prune-containers.sh ${NODES} ${DELAY}

# TODO: Update this scripts!
echo "Running image builder script..."
sh ./docker-build-images.sh ${VERSION}

# TODO: Update this scripts!
echo "Deploying containers"
if [ "$DEPLOY_MODE" = "HOST" ]; then
    echo "Deploying with the same network as the Host (localhost)."
    sh ./docker-deploy-network-host.sh ${NODES} ${DELAY} ${VERSION}
else
    echo "Deploying with network 'eagleeye' is DEPRECATED."
#    sh ./docker-deploy.sh ${NODES} ${DELAY} ${VERSION}
fi

