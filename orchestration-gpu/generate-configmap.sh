# Script: Generate the necessary ConfigMap file for K8S
# Date  : 09/16/2020
# Author: Tim William

#!/bin/bash

# Set working directory to .
dir=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

# Generate Config Map
# 1. ee-ews-cfg
kubectl create configmap ee-ews-cfg --from-file ./config/ews/ews.conf --from-file ./config/ews/site.conf
# 2. ee-scheduler-cfg
kubectl create configmap ee-scheduler-cfg --from-file ./config/scheduler/scheduler.conf --from-file ./config/scheduler/site.conf
# 3. ee-detection-cfg
kubectl create configmap ee-detection-cfg --from-file ./config/detection/detection.conf --from-file ./config/detection/site.conf
# 4. ee-ews-dual-det-cfg
kubectl create configmap ee-ews-dual-det-cfg --from-file ./config/ews-dual-det/site.conf
