kubectl apply -f redis.yaml
kubectl apply -f mongo.yaml
kubectl apply -f ews.yaml
sleep 5
kubectl apply -f detection.yaml
sleep 5
kubectl apply -f scheduler.yaml
sleep 5
kubectl apply -f visualizer.yaml
