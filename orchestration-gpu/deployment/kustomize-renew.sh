kubectl kustomize ./mongo > mongo.yaml
kubectl kustomize ./redis > redis.yaml
kubectl kustomize ./ews > ews.yaml
kubectl kustomize ./detection > detection.yaml
kubectl kustomize ./scheduler > scheduler.yaml
kubectl kustomize ./volume > volume.yaml
kubectl kustomize ./volume-claim > volume-claim.yaml
kubectl kustomize ./service > service.yaml