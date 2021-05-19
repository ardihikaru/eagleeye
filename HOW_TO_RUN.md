# How to run EagleEYE system

## Sample Zenoh PubSub
1. Run Zenoh consumer
    - Root dir: `./core-docker-images/misc/drone_img_publisher`
    - Commands: `$ python data_consumer.py`
2. Run Zenoh publisher
    - Root dir: `./core-docker-images/misc/drone_img_publisher`
    - Commands:
        - Video file:
            - Local (Laptop/PC):
                `$ python data_publisher.py -e tcp/localhost:7446 --cvout -v /home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/videos/samer/0312_1_LtoR_1.mp4`
            - LittleBoy (server with no GUI): 
                `$ python data_publisher.py -e tcp/localhost:7446 -v /home/s010132/devel/eaglestitch/data/videos/samer/0312_1_LtoR_1.mp4`
                `$ python data_publisher.py -e tcp/localhost:7446 -v /home/s010132/devel/eagleeye/data/5g-dive/videos/customTest_MIRC-Roadside-20s.mp4`
        - PC/Laptop's video stream:
            `$ python data_publisher.py -e tcp/localhost:7446 --cvout`

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
    --header 'Content-Type: application/json' \
    --data-raw '{
        "algorithm": "YOLOv3",
        "stream": "ZENOH",
        "uri": "tcp/localhost:7446",
        "scalable": true,
        "extras": {
            "selector": "/eagleeye/svc/**"
        }
    }'
   ```
7. Running Sorter Service:
    - Root dir: `$ ./sorter_service`
    - Command: `$ python sorter.py -c etc/sorter.conf`
8. Start publishing drone data:
    - Emulated with a small script:
        - Root dir: `./core-docker-images/misc/drone_img_publisher`
        - Commands:
            - Video file:
                - Local (Laptop/PC):
                    `$ python data_publisher.py -e tcp/localhost:7446 --cvout -v /home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/videos/samer/0312_1_LtoR_1.mp4`
                - LittleBoy (server with no GUI): 
                    `$ python data_publisher.py -e tcp/localhost:7446 -v /home/s010132/devel/eaglestitch/data/videos/samer/0312_1_LtoR_1.mp4`
            - PC/Laptop's video stream:
                `$ python data_publisher.py -e tcp/localhost:7446 --cvout`

## Running RTSP
- Run: 
    - Littleboy:
        `$ ffmpeg -re -i /home/s010132/devel/eagleeye/data/5g-dive/videos/customTest_MIRC-Roadside-20s.mp4 -rtsp_transport tcp -vcodec h264 -f rtsp rtsp://140.113.86.92/test`
    - Local:
        `$ ffmpeg -re -i /home/s010132/devel/eagleeye/data/5g-dive/videos/customTest_MIRC-Roadside-20s.mp4 -rtsp_transport tcp -vcodec h264 -f rtsp rtsp://localhost/test`
- open video:
    - Littleboy:
        `$ ffplay -rtsp_transport tcp -i rtsp://140.113.86.92/test`
    - Local:
        `$ ffplay -rtsp_transport tcp -i rtsp://localhost/test`
    
## MISC
- Run: `export PYTHONPATH=:/home/s010132/devel/eagleeye/core-service/eagleeye`
- Database related
    - Install mongo tools (to enable `$ mongodump` and `$ mongoexport` command):
        `$ sudo apt install mongo-tools`
    - Install mongo client (to enable `$ mongo` command):
        `$ sudo apt install mongodb-clients`
    - Export database:
        `$ mongodump -h 127.0.0.1 -d eagleeyeDB --out ./db/ --forceTableScan`
    - Export to CSV:
        `$ mongoexport --host localhost --db eagleeyeDB --collection Latency --type=csv --out latency.csv --fields frame_id,category,algorithm,section,latency,node_id,node_name --forceTableScan`
    - Export to JSON:
        `$ mongoexport --host localhost --db eagleeyeDB --collection Latency --type=json --out latency.json --fields frame_id,category,algorithm,section,latency,node_id,node_name --forceTableScan`
