# #  -v redis-data:/data \
docker run -d \
  -h redis \
  -p 6379:6379 \
  --name redis \
  --restart always \
  redis:5.0.5-alpine3.9 /bin/sh -c 'redis-server --appendonly yes'
