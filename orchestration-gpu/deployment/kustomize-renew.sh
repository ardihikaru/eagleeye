kubectl kustomize ./mongo > mongo.yaml
kubectl kustomize ./redis > redis.yaml
kubectl kustomize ./ews > ews.yaml
kubectl kustomize ./detection > detection.yaml
kubectl kustomize ./scheduler > scheduler.yaml
kubectl kustomize . > start-ee.yaml
