# How to run EagleEYE system

## Prerequisite
1. Python version >= 3.8
2. Docker version >= 20.10.6
3. OpenCV CUDA (GPU) >= 4.5.2
4. CUDA version >= 10.1
5. CUDNN Library version (for CUDA 10.1) >= 7.6.5
6. Zenoh version == 0.5.0b8 (**Tested and only work with this version**)

## Project tree
...

## Environment setup
1. Install python library
    - Upgrade pip version: `$ pip3 install --upgrade pip`
    - Go to folder that contains the req file: `cd ./core-docker-images`
    - Install library: `$ pip3 install -r requirements-no-cv.txt`
2. Setup local environment (use `bash` shell):
    `$ . setup-local-env.sh`
    - You can run this following script to see whether mongo and redis services has been ready or not yet:
        - See running containers: `$ docker container ps | grep -service`
        - Sample of running containers:
          ```
          00e43f28aa67   mongo                  "docker-entrypoint.s…"   24 seconds ago   Up 22 seconds           0.0.0.0:27017->27017/tcp, :::27017->27017/tcp   mongo-service
          66012d6c6ba9   5g-dive/redis:1.0      "docker-entrypoint.s…"   24 seconds ago   Up 23 seconds           0.0.0.0:6379->6379/tcp, :::6379->6379/tcp       redis-service  
          ```
        - If your server has no monitor (X Server), use following command instead:
            `$ . setup-local-env.sh 0`
            - Value `0` has no specific meaning. 
            It simply try to trigger adding user `root` to the list of 
            authorised access to the **X server**.
3. Download or clone [eagle data publisher](https://github.com/ardihikaru/eagle-data-publisher) project
   - Place the project under the same ROOT directory with your `EagleEYE` project
        - e.g. `/home/s010132/devel/<HERE>`
4. Each configuration of the micro-service, should be updated accordingly by (1) adding `etc/site.conf` file and
    (2) update `PYTHONPATH` value in file `.env`.
    - We prepared `etc/site.conf.template` file for reference
    - Change the values accordingly and rename them into `etc/site.conf` to apply the changes
    - **FYI**: This `site.conf` will overwrite the default config file (e.g. `etc/ews.conf`)
    - File `.env` is located in the ROOT directory: `/home/s010132/devel/eagleeye/.env`
        - `:/home/s010132/devel/eagleeye/core-service/eagleeye` is from `eagleeye` project
        - `:/home/s010132/devel/eagle-data-publisher/pycore` is from `eagle-data-publisher` project

## How to use in native mode (not containerized)
1. Running EWS Service:
    - Root dir: `$ ./web-service`
    - Command: `$ python3 ews.py -c etc/ews.conf`
    - Wait until it is ready and will have following logs:
      ```
      07-Jul-2021 11:19:35.511672 ERROR ews.gps_collector.service [WARNING!] Unable to connect with 10.194.188.105
      07-Jul-2021 11:19:35.512088 WARNING ews.gps_collector.service [WARNING!] ******* GPS COLLECTOR IS WORKING IN AN OFFLINE MODE !!!!
      07-Jul-2021 11:19:35.512256 WARNING ews.gps_collector.service 
      [11:19:35] Starting thread-level GPS Collector Worker
      07-Jul-2021 11:19:35.513768 WARNING ews.gps_collector.service [11:19:35] Latency for Start threading (1.348 ms)
      07-Jul-2021 11:19:35.514801 WARNING ews.route_manager.module 
      [11:19:35] Initialize RouteManagerModule.
      07-Jul-2021 11:19:35.514979 WARNING ews.gps_collector.service 
      [11:19:35] Initializing GPS Collector Service
      07-Jul-2021 11:19:35.515302 WARNING ews.gps_collector.module 
      [11:19:35] Initialize GPSCollectorModule.
      07-Jul-2021 11:19:35.517627 WARNING ews.gps_collector.service [11:19:35][THREAD-7LWAE] Saving data in every 1 second; GPS data (drone_id=`1`; fly_no=`1`)={'long': 122.5641012, 'lat': 26.0334931, 'alt': 11.0}; Heading=360
      07-Jul-2021 11:19:35.517989 WARNING ews.gps_collector.service 
      07-Jul-2021 11:19:35.562624 WARNING ews.app EagleEYE Web Service is running!
      07-Jul-2021 11:19:36.519868 WARNING ews.gps_collector.service [11:19:36][THREAD-7LWAE] Saving data in every 1 second; GPS data (drone_id=`1`; fly_no=`1`)={'long': 123.5641012, 'lat': 27.0334931, 'alt': 12.0}; Heading=360
      ```
        - You will see a log, such as, `... Saving data in every 1 second ...`.
2. Running PiH Candidate Selection Service:
    - Root dir: `$ ./pih-candidate-selection-service`
    - Command: `$ python3 pcs.py -c etc/pcs.conf`
3. Running PiH Persistance Validation Service (can be multiple, depends on how many num. of connected drones):
    - Root dir: `$ ./pih-persistance-validation-service`
    - Command: `$ python3 pv.py -c etc/pv.conf`
4. Running Detection Service:
    - Root dir: `$ ./object-detection-service`
    - Command: `$ python3 detection.py -c etc/detection.conf`
    - Wait until it is ready:
      ``` 
      [11:22:09][NODE-1] YOLOv3Handler try to subsscribe to channel `node-60e51dce322d5c66b8d52ff9` from [Scheduler Service]
      
      [11:22:09][NODE-1] YOLOv3Handler start listening to [Scheduler Service]
      [11:22:09] Node-1 is ready to serve.
      ```
        - You will see a log, such as, `... Node-1 is ready to serve. ...`.
    - If you want to add more detection services, use following steps:
        1. Register a new node: `$ . register-node.sh <EWS_IP> <EWS_PORT>`
            - File is located in `<PROJECT_DIR>/register-node.sh`
            - In this case, we are registering `Node-2`
            - Sample log:
              ``` 
              $ . register-node.sh localhost 8079
                >>> FYI: Arg[1]=HOST; Arg[2]=PORT 
                >>> Web Service URL is http://localhost:8079
                >>> API to register new node URL is http://localhost:8079/api/nodes 
                >>> Trying to register a new node . . . 
                {"success": true, "message": "Registration of a new Node is success.", "data": {"candidate_selection": true, "persistence_validation": true, "name": "2", "id": "60e51faf322d5c66b8d52ffa", "created_at": "2021-07-07, 11:29:51", "updated_at": "2021-07-07, 11:29:51"}, "status": 200}
                >>> Registering a new node succeed
              ```
        2. Run detection service: `$ python3 detection.py -c etc/detection.conf`
        3. Repeat step-1 and step-2 to register another new nodes (e.g. `Node-3`)
5. Running Data Offloader Service:
    - Root dir: `$ ./data_offloader_service`
    - Command: `$ python3 offloader.py -c etc/offloader.conf`
6. Running Sorter Service:
    - Root dir: `$ ./sorter_service`
    - Command: `$ python3 sorter.py -c etc/sorter.conf`
7. Running Visualizer Service:
    - Root dir: `$ ./visualizer-service`
    - Command: `$ python3 visualizer.py -c etc/visualizer.conf`
8. Start EagleEYE drone data consumer:
    - Run: `$ . start-eagleeye-consumer.sh`
        - File located in `<PROJECT_DIR>/start-eagleeye-consumer.sh`
    - Sample log:
       ``` 
       $ . start-eagleeye-consumer.sh localhost 8079 tcp/localhost:7446
       >>> FYI: Arg[1]=HOST; Arg[2]=PORT; Arg[3]=ZENOHHOST 
       >>> Web Service URL is http://localhost:8079
       >>> Zenoh Host: tcp/localhost:7446
       >>> Trying to start consumer . . . 
       {"success": true, "message": "OK", "data": {"algorithm": "YOLOv3", "stream": "ZENOH", "uri": "tcp/localhost:7446", "scalable": true, "extras": {"selector": "/eagle/svc/**"}}, "status": 200}
       >>> Starting EagleEYE Drone Data Consumer
       ```
9. Start publishing drone data:
    - Go to `eagle data publisher` project dir: `$ cd /home/s010132/devel/eagle-data-publisher`
    - Run publisher: `$ env RUST_LOG=debug python3 data_publisher.py -e tcp/localhost:7446 --resize`
        - If you try them in the same PC, you can use `localhost`
        - If you use to test them to PubSub with different PCs, change them to **IP of the Consumer**
        - By default, it read your local camera (video0).
        - If you want to extract frames from a video file, use following command:
            `$ env RUST_LOG=debug python3 data_publisher.py -e tcp/localhost:7446 --resize -v >your_video_path>`
        - if you want to resize the video property, let say, to FullHD, follow this steps:
            - Run this to know possible resolution and its FPS (In Linux only):
                `$ v4l2-ctl --list-formats-ext`
            - To apply the config, you can try following command:
              ```
              $ env RUST_LOG=debug python3 data_publisher.py -e tcp/localhost:7446 --resize --pwidth 1920 --pheight 1080 -v >your_video_path>
              ```

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
    
## How to use in docker mode (containerized)
1. Initially, please build followring Dockerfile(s):
   - In folder `./core-docker-images`, run:
     ```
     $ docker build -t 5g-dive/eagleeye/nvidia-gpu-opencv:2.4 .
     ```
   - In folder `./core-service/`, run:
     - File `Dockerfile`: `$ docker build -t 5g-dive/eagleeye/core-service:2.4 .`
     - File `Dockerfile-compact`: `$ docker build -f Dockerfile-compact -t 5g-dive/eagleeye/pycore-compact:1.0 .`
2. Deploy containerized RedisDB and MongoDB Services:
    - Run: `$ . setup-local-env.sh`
    - Destroy: `$ . docker-prune-containers.sh`
3. Web Service (EWS)
    - Build: `$ docker build -t 5g-dive/eagleeye/web-service:2.4 .`
    - Run:
      ``` 
      $ docker run --name ews-service -d \
          --network host \
          -v /home/s010132/devel/eagleeye/web-service/etc/site-docker.conf:/app/etc/site.conf \
          -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
          5g-dive/eagleeye/web-service:2.4
      ```
4. Sorter Service (can be multiple)
    - Folder Loc: `./sorter_service/`
    - Build: `$ docker build -f Dockerfile -t 5g-dive/eagleeye/sorter:1.0 .`
    - Run: `$ docker run --name <svc-name> -d --network host -v <site-config-fullpath>:/app/etc/site.conf 5g-dive/eagleeye/sorter:1.0`
        - Example of `Sorter 1`: `$ docker run --name sorter-1-svc -d --network host -v /home/s010132/devel/eagleeye/sorter_service/etc/site-1.conf:/app/etc/site.conf 5g-dive/eagleeye/sorter:1.0`
        - Example of `Sorter 2`: `$ docker run --name sorter-2-svc -d --network host -v /home/s010132/devel/eagleeye/sorter_service/etc/site-2.conf:/app/etc/site.conf 5g-dive/eagleeye/sorter:1.0`
        - Example of `Sorter 3`: `$ docker run --name sorter-3-svc -d --network host -v /home/s010132/devel/eagleeye/sorter_service/etc/site-3.conf:/app/etc/site.conf 5g-dive/eagleeye/sorter:1.0`
5. PiH Candidate Selection (PCS) Service
    - Folder Loc: `./pih-candidate-selection-service/`
    - build: `$ docker build -f Dockerfile -t 5g-dive/eagleeye/pcs:1.0 .`
    - Run: `$ docker run --name <svc-name> --network host -d -v <site-config-fullpath>:/app/etc/site.conf 5g-dive/eagleeye/pcs:1.0`
        - Example: `$ docker run --name pcs-svc --network host -d -v /home/s010132/devel/eagleeye/pih-candidate-selection-service/etc/site.conf:/app/etc/site.conf 5g-dive/eagleeye/pcs:1.0`
6. PiH Persistance Validation (PV) Service (can be multiple)
    - Folder Loc: `./pih-persistance-validation-service/`
    - Build: `$ docker build -f Dockerfile -t 5g-dive/eagleeye/pv:1.0 .`
    - Run: `$ docker run --name <svc-name> --network host -d -v <site-config-fullpath>:/app/etc/site.conf 5g-dive/eagleeye/pv:1.0`
        - Example of `PV 1`: `$ docker run --name pv-1-svc --network host -d -v /home/s010132/devel/eagleeye/pih-persistance-validation-service/etc/site-1.conf:/app/etc/site.conf 5g-dive/eagleeye/pv:1.0`
        - Example of `PV 2`: `$ docker run --name pv-2-svc --network host -d -v /home/s010132/devel/eagleeye/pih-persistance-validation-service/etc/site-2.conf:/app/etc/site.conf 5g-dive/eagleeye/pv:1.0`
        - Example of `PV 3`: `$ docker run --name pv-3-svc --network host -d -v /home/s010132/devel/eagleeye/pih-persistance-validation-service/etc/site-3.conf:/app/etc/site.conf 5g-dive/eagleeye/pv:1.0`
7. Detection Service (can be multiple)
    - Build: 
        - Parent Docker: `$ docker build -f Dockerfile-parent -t 5g-dive/eagleeye/dual-object-detection-service-head:2.4 .`
        - Child Docker: `$ docker build -t 5g-dive/eagleeye/dual-object-detection-service:2.4 .`
    - **IMPORTANT**: 
        1. Please make sure that following folder exist:
        `/home/s010132/devel/eagle-data-publisher/pycore/eagle_zenoh`
            - if does not yet, copy it first:
                `$ cp -fr /home/s010132/devel/eagle-data-publisher/pycore/eagle_zenoh eagle_zenoh`
        2. After deploying `detection 1`, always run `. register-node.sh` first, 
            before deploying detection sevice 2 onwards.
    - Run: 
        - Detection 1:
          ```
          $ docker run --runtime=nvidia --name "detection-service-1" -d \
              --network host \
              -v /home/s010132/devel/eagleeye/object-detection-service/etc/site-docker.conf:/app/etc/site.conf \
              -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
              5g-dive/eagleeye/dual-object-detection-service:2.4
          ```
        - Detection 2:
          ```
          $ docker run --runtime=nvidia --name "detection-service-2" -d \
              --network host \
              -v /home/s010132/devel/eagleeye/object-detection-service/etc/site-docker.conf:/app/etc/site.conf \
              -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
              5g-dive/eagleeye/dual-object-detection-service:2.4
          ```
        - Detection 3:
          ```
          $ docker run --runtime=nvidia --name "detection-service-3" -d \
              --network host \
              -v /home/s010132/devel/eagleeye/object-detection-service/etc/site-docker.conf:/app/etc/site.conf \
              -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
              5g-dive/eagleeye/dual-object-detection-service:2.4
          ```
        - Detection 4:
          ```
          $ docker run --runtime=nvidia --name "detection-service-4" -d \
              --network host \
              -v /home/s010132/devel/eagleeye/object-detection-service/etc/site-docker.conf:/app/etc/site.conf \
              -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
              5g-dive/eagleeye/dual-object-detection-service:2.4
          ```
        - Detection 5:
          ```
          $ docker run --runtime=nvidia --name "detection-service-5" -d \
              --network host \
              -v /home/s010132/devel/eagleeye/object-detection-service/etc/site-docker.conf:/app/etc/site.conf \
              -v /home/s010132/devel/eagleeye/object-detection-service/config_files:/app/config_files \
              5g-dive/eagleeye/dual-object-detection-service:2.4
          ```
      - Change `detection-service-1` into `detection-service-x` to deploy more
8. Offloader Service
    - Build: `$ docker build -t 5g-dive/eagleeye/offloader-service:2.4 .`
    - Run:
      ``` 
      $ docker run --name offloader-service -d \
          --network host \
          -v /home/s010132/devel/eagleeye/data_offloader_service/etc/site-docker.conf:/app/etc/site.conf \
          5g-dive/eagleeye/offloader-service:2.4
      ```
      - Then, run following script in terminal:
        ``` 
        curl --location --request POST 'http://localhost:8079/api/stream/live' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "algorithm": "YOLOv3",
            "stream": "ZENOH",
            "uri": "tcp/localhost:7446",
            "scalable": true,
            "extras": {
                "selector": "/eagle/svc/**"
            }
        }'
        ```
        - Where `localhost` is the IP of the deployed **Web Service**
9. Visualizer Service (can be multiple)
    - Folder Loc: `./visualizer-service/`
    - Build: `$ docker build -t 5g-dive/eagleeye/visualizer-service:2.4 .`
    - Run:
        - For **Drone 1**:
            - Drone 1 (RTSP EE):
              ```
              $ docker run --name "viz-rtsp-ee-svc-1" -d \
                  --network host \
                  -v /home/s010132/devel/eagleeye/visualizer-service/etc/site-rtsp-1.conf:/app/etc/site.conf \
                  5g-dive/eagleeye/visualizer-service:2.4
              ```
            - Drone 1 (RTSP RAW): 
              ```
              $ docker run --name "viz-rtsp-raw-svc-1" -d \
                  --network host \
                  -v /home/s010132/devel/eagleeye/visualizer-service/etc/site-rtsp-raw-1.conf:/app/etc/site.conf \
                  5g-dive/eagleeye/visualizer-service:2.4
              ```
        - For **Drone 2**:
            - Drone 2 (RTSP EE):
              ```
              $ docker run --name "viz-rtsp-ee-svc-2" -d \
                  --network host \
                  -v /home/s010132/devel/eagleeye/visualizer-service/etc/site-rtsp-2.conf:/app/etc/site.conf \
                  5g-dive/eagleeye/visualizer-service:2.4
              ```
            - Drone 2 (RTSP RAW): 
              ```
              $ docker run --name "viz-rtsp-raw-svc-2" -d \
                  --network host \
                  -v /home/s010132/devel/eagleeye/visualizer-service/etc/site-rtsp-raw-2.conf:/app/etc/site.conf \
                  5g-dive/eagleeye/visualizer-service:2.4
              ```
10. Start video stream consumer
    - Run this command:
      ``` 
      curl --location --request POST 'http://localhost:8079/api/stream/live' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "algorithm": "YOLOv3",
            "stream": "ZENOH",
            "uri": "tcp/192.168.1.60:7446",
            "scalable": true,
            "extras": {
                "selector": "/eagle/svc/**"
            }
        }'
      ``` 
      - Please change `localhost` value accordingly.

## MISC
- Tunnel to LittleBoy:
    - Local: `$ ssh -L 5901:127.0.0.1:5901 -C -N -l s010132 192.168.1.10`
    - Public IP: `$ ssh -L 5901:127.0.0.1:5901 -C -N -l s010132 140.113.86.92`
    - password: `s010132`
- Tunnel to Fatman:
    `$ ssh -L 5901:127.0.0.1:5901 -C -N -l   192.168.1.60`
    - password: `k200user`
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
- [Disable sudoers in docker command](https://www.codegrepper.com/code-examples/shell/how+to+remove+sudo+from+docker+command)
- [Install Nvidia-Docker](https://cnvrg.io/how-to-setup-docker-and-nvidia-docker-2-0-on-ubuntu-18-04/):
  1. setting the GPG and remote repo for the package
     ``` 
     $ curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
          sudo apt-key add -
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
        curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
          sudo tee /etc/apt/sources.list.d/nvidia-docker.list
     ```
  2. update the apt lists
     ``` 
     $ sudo apt-get update
     ```
  3. Now you install nvidia-docker (2) and reload the Docker daemon configurations
     ``` 
     $ sudo apt-get install -y nvidia-docker2
     $ sudo pkill -SIGHUP dockerd
     ```
  5. Now, test: 
     ``` 
     $ docker run --runtime=nvidia --rm nvidia/cuda:9.0-base nvidia-smi
     ```
     - The output should look something like this:
       ``` 
        +-----------------------------------------------------------------------------+
        | NVIDIA-SMI 390.77                 Driver Version: 390.77                    |
        |-------------------------------+----------------------+----------------------+
        | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
        | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
        |===============================+======================+======================|
        |   0  Tesla K80           Off  | 00000000:00:1E.0 Off |                    0 |
        | N/A   39C    P0    83W / 149W |      0MiB / 11441MiB |     98%      Default |
        +-------------------------------+----------------------+----------------------+
                                                                                       
        +-----------------------------------------------------------------------------+
        | Processes:                                                       GPU Memory |
        |  GPU       PID   Type   Process name                             Usage      |
        |=============================================================================|
        |  No running processes found                                                 |
        +-----------------------------------------------------------------------------+
       ```
  6. Congrats! You have successfully installed Docker and Nvidia-Docker in your environment.
