## How to test side-by-side performance

## How to:
1. Run `EasyDarwin` RTSP Server
2. Simulate video stream. Run file: `$ ./misc/rtsp_sender/rtsp_image_publisher.py`
3. **Visualize** input video stream, run: `$ ffplay rtsp://localhost/test`
4. Run visulizer service
5. Run ZMQ Serder: `$ ./misc/zmq_sender/zmq_sender.py`
6. **Visualize** CV.out version: `$ ./misc/video_stream_reader/opencv_reader.py`
7. **Visualize** visualizer RTSP version: `$ ffplay rtsp://localhost/test`