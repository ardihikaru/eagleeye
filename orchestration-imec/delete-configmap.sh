# Script: Delete EagleEYE Orchestration ConfigMap
# Date  : 09/11/2020
# Author: Tim William

#!/bin/bash
kubectl delete configmap ee-ews-cfg
kubectl delete configmap ee-scheduler-cfg
kubectl delete configmap ee-detection-cfg