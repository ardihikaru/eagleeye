# How to run EagleEYE system

## In native mode (not containerized)
1. Setup local environment (use `bash` shell):
    `$ . setup-local-env.sh`
2. Running EWS Service:
    - Root dir: `$ ./web-service`
    - Command: `$ python ews.py -c etc/ews.conf`
3. Running Detection Service:
    - Root dir: `$ ./object-detection-service`
    - Command: `$ python detection.py -c etc/detection.conf`
4. Running Scheduler Service:
    - Root dir: `$ ./scheduler_service`
    - Command: `$ python scheduler.py -c etc/scheduler.conf`
5. Running Visualizer Service:
    - Root dir: `$ ./visualizer-service`
    - Command: `$ python visualizer.py -c etc/visualizer.conf`
6. Start drone data consumer from Scheduler Service, via **Web Service**:
   ``` 
   curl --location --request POST 'http://localhost:8079/api/stream/live' \
    --header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiYXJkaTphcmRpIiwiZXhwIjoxNTk1OTU4NTY5fQ.iM9MsPnielanuPOHK_P2EhC7HB0SSs8j-bhtVvM3ARY' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "algorithm": "YOLOv3",
        "stream": "ZENOH",
        "uri": "tcp/localhost:7446",
        "scalable": true,
        "extras": {
            "selector": "/eagleeye/img/**"
        }
    }'
   ```
7. Start publishing drone data:
    - Emulated with a small script:
        - Root dir: `./core-docker-images/misc/drone_img_publisher`
        - Commands:
            - Video file:
                `$ python data_publisher.py -e tcp/localhost:7446 --cvout -v /home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/videos/samer/0312_1_LtoR_1.mp4`
            - PC/Laptop's video stream:
                `$ python data_publisher.py -e tcp/localhost:7446 --cvout`
