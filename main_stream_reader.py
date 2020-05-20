from __future__ import division
import argparse
from libs.addons.streamer.video_streamer import VideoStreamer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto_restart', type=bool, default=False, help='Auto Restart reader video')
    parser.add_argument('--disable_delay', type=bool, default=True, help='Enable/disable delay')
    parser.add_argument('--start_frame_id', type=int, default=1, help='Start frame ID')
    parser.add_argument('--max_frames', type=int, default=57, help='Max Frames; Ignored when `is_unlimited`=True')
    parser.add_argument('--is_unlimited', type=bool, default=True, help='Loop forever')

    parser.add_argument('--pih_location_fetcher_port', type=int, default=5571, help='ZMQ Viewer port PLF')
    parser.add_argument('--visualizer_origin_port', type=int, default=5580, help='ZMQ Viewer port Original Visualizer')

    # Better do not change this
    parser.add_argument("--enable_cv_out", type=bool, default=True,
                        help="Enable/disable Output video streaming; run `viewer.py` to see the results")

    # Change to fit your need / scenario
    parser.add_argument('--visual_type', type=int, default=3, help='Type_1=YOLO; 2=MOD; 3=YOLO+MOD; otherwise=No BBox')

    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument("--total_workers", type=int, default=1, help="path to dataset")

    # parser.add_argument("--delay", type=int, default=4, help="Send frame into YOLO Network in every <delay> frames.")
    parser.add_argument("--delay", type=int, default=1, help="Send frame into YOLO Network in every <delay> frames.")

    parser.add_argument("--output_folder", type=str, default="output/original/", help="path to save raw images")

    # To show the result in GUI (Copied from worker_yolov3.py configuration)
    parser.add_argument('--mbbox_output', type=str, default="output/mbbox",
                        help='MMBox image output')
    parser.add_argument('--normal_output', type=str, default="output/bbox/",
                        help='Folder location to store bbox image')

    # YOLOv3 default configuration
    parser.add_argument('--device', default='', help='device id (i.e. 0 or 0,1) or cpu')
    parser.add_argument('--half', action='store_true', help='half precision FP16 inference')
    parser.add_argument("--img_size", type=int, default=416, help="size of each image dimension")
    # parser.add_argument("--img_size", type=int, default=832, help="size of each image dimension")

    # Used only when source_type = "folder", otherwise it's not used
    parser.add_argument("--source_folder_prefix", type=str, default="out", help="source folder prefix")

    # parser.add_argument("--source_type", type=str, default="folder", help="source type")
    parser.add_argument("--source_type", type=str, default="streaming", help="source type")

    # parser.add_argument("--source", type=str, default="data/5g-dive/57-frames/", help="source")
    # parser.add_argument("--source", type=str, default="data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4", help="source")
    # parser.add_argument("--source", type=str, default="data/5g-dive/videos/customTest_MIRC-Roadside-20s.mp4", help="source")
    # parser.add_argument("--source", type=str, default="data/5g-dive/videos/customDrone_MIRC-Entrance-Hover-1m.MP4", help="source")
    parser.add_argument("--source", type=str, default="data/5g-dive/videos/demo_video.MP4", help="source")
    # parser.add_argument("--source", type=str, default="http://127.0.0.1:10000/stream-1.flv", help="source")
    # parser.add_argument("--source", type=str, default="http://192.168.0.50:10000/drone-1.flv", help="source")
    # parser.add_argument("--source", type=str, default="http://192.168.42.1/live", help="source")
    opt = parser.parse_args()
    # print(opt)

    VideoStreamer(opt).run()
