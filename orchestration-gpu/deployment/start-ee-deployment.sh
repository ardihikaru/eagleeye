echo "[START] Starting EagleEYE deployment ..."

echo "[INFO] Init databases ..."
kubectl apply -f redis.yaml
sleep 1

kubectl apply -f mongo.yaml
sleep 1

echo "[INFO] Web Service ..."
kubectl apply -f ews.yaml
sleep 3

echo "[INFO] Worker-1 ..."
kubectl apply -f detection.yaml
sleep 5

echo "[INFO] Registering Worker-1 ..."
sh register-node.sh
sleep 2

echo "[INFO] Worker-2 ..."
kubectl apply -f detection-2.yaml
sleep 5

echo "[INFO] Scheduler ..."
kubectl apply -f scheduler.yaml
sleep 5

echo "[INFO] Visualizer ..."
kubectl apply -f visualizer.yaml
sleep 2

echo "[INFO] All things go!"
