#!/bin/bash

echo "[INFO] Starting NCTU EagleEYEv1.5 Deployment ..."
kubectl create -f namespace-eagleeye.yaml

# echo "[INFO] Creating Docker Hub credentials ..."
kubectl apply -f timwilliam-regcred.yaml

echo "[INFO] - Creating Volume and VolumeClaim ..."
kubectl apply -f volume.yaml
sleep 4
kubectl apply -f volume-claim.yaml
sleep 4

echo "[INFO] - Creating the Databases: redis-deploy and mongo-deploy ..."
kubectl apply -f redis.yaml
kubectl apply -f mongo.yaml

kubectl apply -f service.yaml # comment out if service is not used
sleep 3

echo "[INFO] - Creating the Web Service: ews-deploy ..."
kubectl apply -f ews.yaml
sleep 20

echo "[INFO] - Creating the Detection: detection-deploy ..."
kubectl apply -f detection.yaml
sleep 4

echo "[INFO] - Registering Worker-1 ..."
sh register-node.sh
sleep 1

echo "[INFO] - Creating the Detection: detection-deploy-2 ..."
kubectl apply -f detection-2.yaml
sleep 4

echo "[INFO] - Registering Worker-2 ..."
sh register-node.sh
sleep 1

echo "[INFO] - Creating the Detection: detection-deploy-3 ..."
kubectl apply -f detection-3.yaml
sleep 4

echo "[INFO] - Creating the Scheduler: scheduler-deploy ..."
kubectl apply -f scheduler.yaml
sleep 4

echo "[INFO] - Creating the Detection: visualizer-deploy ..."
kubectl apply -f visualizer.yaml
sleep 3

echo "[INFO] - Creating the Detection: visualizer-deploy-raw ..."
kubectl apply -f visualizer-raw.yaml
sleep 3

echo "[INFO] All things ready to go! Go run the scripts now!"
