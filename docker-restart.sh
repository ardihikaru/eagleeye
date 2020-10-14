#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
NODES=$1
DELAY=$2

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
      DELAY=2  # default value
else
      echo "\$DELAY is NOT empty"
fi

echo "Running shell script file: docker-prune.sh"
sh ./docker-prune.sh ${NODES} ${DELAY}

echo "Running shell script file: docker-deploy.sh"
sh ./docker-deploy.sh