echo "[START] Starting EagleEYE deployment ..."
kubectl delete deployments --all
kubectl delete svc --all
kubectl delete configmap --all

kubectl apply -f service.yaml

echo "[INFO] Init databases ..."
kubectl apply -f redis.yaml
sleep 2

kubectl apply -f mongo.yaml
sleep 2

echo "[INFO] Web Service ..."
kubectl apply -f ews.yaml
sleep 20

echo "[INFO] Worker-1 ..."
kubectl apply -f detection.yaml
sleep 7

echo "[INFO] Scheduler ..."
kubectl apply -f scheduler.yaml
sleep 3

echo "[INFO] Visualizer ..."
kubectl apply -f visualizer.yaml
sleep 3

echo "[INFO] Visualizer RAWWWWR ..."
#kubectl apply -f visualizer-raw.yaml
#sleep 3

echo "[INFO] All things go!"
