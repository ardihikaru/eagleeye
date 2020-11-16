echo "[START] Starting EagleEYE deployment ..."
kubectl delete deployments --all
kubectl delete svc --all
kubectl delete configmap --all

echo "[INFO] Init databases ..."
kubectl apply -f redis.yaml
#kubectl apply -f redis/redis-service.yaml
sleep 2

kubectl apply -f mongo.yaml
#kubectl apply -f mongo/mongo-service.yaml
sleep 2

echo "[INFO] Web Service ..."
kubectl apply -f ews.yaml
#kubectl apply -f ews/ews-service.yaml
sleep 15

echo "[INFO] Worker-1 ..."
kubectl apply -f detection.yaml
sleep 10

echo "[INFO] Registering Worker-1 ..."
sh register-node.sh
sleep 2

echo "[INFO] Worker-2 ..."
kubectl apply -f detection-2.yaml
sleep 10

echo "[INFO] Registering Worker-2 ..."
sh register-node.sh
sleep 2

echo "[INFO] Worker-3 ..."
kubectl apply -f detection-3.yaml
sleep 10

echo "[INFO] Scheduler ..."
kubectl apply -f scheduler.yaml
#kubectl apply -f scheduler/scheduler-service.yaml
sleep 3

echo "[INFO] Visualizer ..."
kubectl apply -f visualizer.yaml
sleep 3

echo "[INFO] Visualizer RAWWWWR ..."
kubectl apply -f visualizer-raw.yaml
sleep 3


echo "[INFO] All things go!"
