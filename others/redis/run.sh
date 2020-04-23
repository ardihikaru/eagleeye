# #  -v redis-data:/data \
docker run -d \
  -h redis \
  -e REDIS_PASSWORD=bismillah \
  -p 6379:6379 \
  --name redis \
  --restart always \
  5g-dive/redis:1.0 /bin/sh -c 'redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}'
