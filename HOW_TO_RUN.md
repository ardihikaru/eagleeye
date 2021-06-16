# How to run EagleEYE system

## Enviroment in LittleBoy Server
- Tunnel to enable Remmina:
    `$ ssh -L 5901:127.0.0.1:5901 -C -N -l s010132 140.113.86.92`

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
- Tunnel to LittleBoy:
    `$ ssh -L 5901:127.0.0.1:5901 -C -N -l s010132 192.168.1.10`
    - password: `s010132`
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
- When error in Jetson nano:
  ```
  >>> import numpy                                                                                                                                                                       
    Traceback (most recent call last):                                                                                                                                                     
      File "/usr/lib/python3/dist-packages/numpy/core/__init__.py", line 16, in <module>                                                                                                   
        from . import multiarray                                                                                                                                                           
    ImportError: cannot import name 'multiarray' from partially initialized module 'numpy.core' (most likely due to a circular import) (/usr/lib/python3/dist-packages/numpy/core/__init__.
    py)                                                                                                                                                                                    
                                                                                                                                                                                           
    During handling of the above exception, another exception occurred:                                                                                                                    
                                                                                                                                                                                           
    Traceback (most recent call last):                                                                                                                                                     
      File "<stdin>", line 1, in <module>                                                                                                                                                  
      File "/usr/lib/python3/dist-packages/numpy/__init__.py", line 142, in <module>                                                                                                       
        from . import add_newdocs                                                                                                                                                          
      File "/usr/lib/python3/dist-packages/numpy/add_newdocs.py", line 13, in <module>                                                                                                     
        from numpy.lib import add_newdoc                                                                                                                                                   
      File "/usr/lib/python3/dist-packages/numpy/lib/__init__.py", line 8, in <module>                                                                                                     
        from .type_check import *                                                                                                                                                          
      File "/usr/lib/python3/dist-packages/numpy/lib/type_check.py", line 11, in <module>                                                                                                  
        import numpy.core.numeric as _nx                                                                                                                                                   
      File "/usr/lib/python3/dist-packages/numpy/core/__init__.py", line 26, in <module>                                                                                                   
        raise ImportError(msg)
  
    ImportError: 
    Importing the multiarray numpy extension module failed.  Most
    likely you are trying to import a failed build of numpy.
    If you're working with a numpy git repo, try `git clean -xdf` (removes all
    files not under version control).  Otherwise reinstall numpy.
    
    Original error was: cannot import name 'multiarray' from partially initialized module 'numpy.core' (most likely due to a circular import) (/usr/lib/python3/dist-packages/numpy/core/__
    init__.py)
  ```
  - Solution [here](https://stackoverflow.com/questions/53135410/importerror-cannot-import-name-multiarray):   
    - Step 1: `$ sudo -H python3 -m pip uninstall numpy`
        - When this issue happens: `Not uninstalling numpy at /usr/lib/python3/dist-packages, outside environment /usr`
        - Then, **SKIP** step 1.
    - Step 2: `$ sudo apt purge python3-numpy`
    - Step 3: `$ sudo -H python3 -m pip install --upgrade pip`
    - Step 4: `$ sudo -H python3 -m pip install numpy`
- Install JTOP in Jetson Nano: `$ sudo -H pip3 install jetson-stats`
    - how to use: `$ sudo jtop`
- How to [check camera's specification](https://www.twblogs.net/a/5d6687a0bd9eee5327feb721):
    - Run: `$ v4l2-ctl --list-formats-ext`
- How to use [compressed version/MJPEG](https://github.com/opencv/opencv/issues/11324#issuecomment-436016969):
    - dxxx
- How to use [EasyDarwin RTSP Server](https://github.com/EasyDarwin/EasyDarwin):
    - Start server: `$ ./start.sh`
    - Stop server: `$ ./stop.sh`
