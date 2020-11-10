
## How to run in docker 
1. `eagleeye` Network
```
docker network create -d bridge eagleeye
```

2. MongoDB
```
docker run -d -p 27017:27017 --name mongo-service --network eagleeye mongo
```

3. RedisDB
```
docker run -d \
  -h redis \
  -p 6379:6379 \
  --name redis-service \
  --restart always \
  --network eagleeye \
  5g-dive/redis:1.0 /bin/sh -c 'redis-server --appendonly yes'
```

4. WEB SERVICE
```
docker run --name ews-service -d \
  --network eagleeye \
  -p 8080:8080 \
  -v /home/s010132/devel/eagleeye/web-service/etc/ews.conf:/conf/ews/ews.conf \
  -v /home/s010132/devel/eagleeye/site_conf_files/web-service/site.conf:/conf/ews/site.conf \
  -v /home/s010132/devel/eagleeye/site_conf_files/object-detection-service/site.conf:/conf/dual-det/site.conf \
  5g-dive/eagleeye/web-service:2.3
```

5. DUAL DET
```
docker run --runtime=nvidia --name detection-service-1 -d \
  --network eagleeye \
  -v /home/s010132/devel/eagleeye/object-detection-service/etc/detection.conf:/conf/dual-det/detection.conf \
  -v /home/s010132/devel/eagleeye/site_conf_files/object-detection-service/site.conf:/conf/dual-det/site.conf \
  -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
  5g-dive/eagleeye/dual-object-detection-service:2.3
```

6. SCHEDULER
```
docker run --name scheduler-service -d \
  --network eagleeye \
  -v /home/s010132/devel/eagleeye/scheduler-service/etc/scheduler.conf:/conf/scheduler/scheduler.conf \
  -v /home/s010132/devel/eagleeye/site_conf_files/scheduler-service/site.conf:/conf/scheduler/site.conf \
  -v /home/s010132/devel/eagleeye/data:/app/data \
  5g-dive/eagleeye/scheduler-service:2.3
```

7. VISUALIZER
```
docker run --name visualizer-service -d \
  --network eagleeye \
  -v /home/s010132/devel/eagleeye/visualizer-service/etc/visualizer.conf:/conf/visualizer/visualizer.conf \
  -v /home/s010132/devel/eagleeye/site_conf_files/visualizer-service/site.conf:/conf/visualizer/site.conf \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  5g-dive/eagleeye/visualizer-service:2.3
```


### MISC
- PING
```
docker run --rm 5g-dive/eagleeye/scheduler-service:1.0 apt-get install iputils-ping -y; ping ews
```
