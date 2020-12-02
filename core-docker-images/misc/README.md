## FYI
- **Terminal 1**: Deploy EagleEYE System
- **Terminal 2**: Simply used only to see and verify 
    that EagleEYE is working perfectly

## Important EagleEYE Configuration:
- <YOUR_DIR>/eagleeye/site_conf_files/scheduler-service/site.conf:
    - `num_skipped_frames`=`3`; It skipped every 3 frames. 
        - i.e. only take frames: `{1, 4, 8, ...}` 

## How to use EagleEYE System
1. Open **terminal 1**, and do following steps:
    - go to `eagleeye` project directory
2. In **terminal 1**, deploy `eagleeye`: 
    `$ . docker-restart.sh 1 HOST`
    - `1` here means, deploying 1 `YOLOv3` App;
        you may change it **into 2 or more**.
3. In **terminal 2**, see what's the `Scheduler Service` do:
    - `$ docker logs -f scheduler-service`
    - You will see:
   ```
   ...
   Latency [Creating Redis variable] in: (1.14393 ms)

   [22:51:37] ReaderHandler try to consume the published data 
   ```
4. You may start sending UDP to the Server
    - At this point, please make sure that can really read your UDP Stream, by:
        - Open file `<YOUR_DIR>/eagleeye/core-docker-images/misc/video_stream_reader/opencv_reader.py`
        - Change value `cap` into: `cap = cv.VideoCapture("udp://localhost:6000")`
        - Run this script (**don't forget to enable virtual Env!**):
            `$ python opencv_reader.py`
        - If it runs perfectly, then, it is okay. you can relax and stop this script from running.
5. In **terminal 1**, start reading UDP Stream:
    `$ . exec-streaming.sh udp://localhost:6000`
    - In **terminal 2**, you will see that `Scheduler Service` 
        is currently reading your images
6. Enjoy!
