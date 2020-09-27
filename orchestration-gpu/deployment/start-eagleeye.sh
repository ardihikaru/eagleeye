#!/bin/bash

echo "[INFO] Starting NCTU EagleEYEv1.5 Deployment ..."

# echo "[INFO] Creating Docker Hub credentials ..."
#kubectl apply -f timwilliam-regcred.yaml

echo "[INFO] - Creating Volume and VolumeClaim ..."
kubectl apply -f volume.yaml
kubectl apply -f volume-claim.yaml
sleep 2

echo "[INFO] - Creating the Service (you know, for communication) ..."
kubectl apply -f service.yaml
sleep 1

echo "[INFO] - Creating the Databases: redis-deploy and mongo-deploy ..."
kubectl apply -f redis.yaml
kubectl apply -f mongo.yaml
sleep 2

echo "[INFO] - Creating the Web Service: ews-deploy ..."
kubectl apply -f ews.yaml
sleep 3

echo "[INFO] - Creating the Scheduler: scheduler-deploy ..."
kubectl apply -f scheduler.yaml
sleep 2

echo "[INFO] - Creating the Detection: detection-deploy ..."
kubectl apply -f detection.yaml
sleep 3

echo "[INFO] All things ready to go! Go run the scripts now!"
