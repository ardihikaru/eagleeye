from __future__ import division
import argparse
from libs.addons.streamer.video_streamer import VideoStreamer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto_restart', type=bool, default=False, help='Auto Restart reader video')
    parser.add_argument('--disable_delay', type=bool, default=True, help='Enable/disable delay')

    # parser.add_argument('--start_frame_id', type=int, default=601, help='Start frame ID')
    parser.add_argument('--start_frame_id', type=int, default=1, help='Start frame ID')
    # parser.add_argument('--start_frame_id', type=int, default=11, help='Start frame ID')

    # parser.add_argument('--max_frames', type=int, default=18, help='Max Frames')
    # parser.add_argument('--max_frames', type=int, default=24, help='Max Frames')
    # parser.add_argument('--max_frames', type=int, default=60, help='Max Frames')
    # parser.add_argument('--max_frames', type=int, default=300, help='Max Frames')
    parser.add_argument('--max_frames', type=int, default=57, help='Max Frames; Set value=0 to have unlimited loop')

    # parser.add_argument('--drone_id', type=int, default=3, help='Drone ID')
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument('--device', default='', help='device id (i.e. 0 or 0,1) or cpu')
    # parser.add_argument("--total_workers", type=int, default=6, help="path to dataset")
    # parser.add_argument("--total_workers", type=int, default=3, help="path to dataset")
    parser.add_argument("--total_workers", type=int, default=1, help="path to dataset")

    # parser.add_argument("--enable_cv_out", type=bool, default=False, help="Enable/disable Output video streaming")
    parser.add_argument("--enable_cv_out", type=bool, default=True, help="Enable/disable Output video streaming")

    parser.add_argument("--enable_mbbox", type=bool, default=True, help="Enable/disable Output MB-Box-based video streaming")

    parser.add_argument("--delay", type=int, default=4, help="path to dataset")
    # parser.add_argument("--delay", type=int, default=7, help="path to dataset")
    # parser.add_argument("--delay", type=int, default=1, help="path to dataset")
    # parser.add_argument("--delay", type=int, default=2, help="path to dataset")

    parser.add_argument("--output_folder", type=str, default="hasil/media/ramdisk/output_frames/", help="path to save raw images")

    # To show the result in GUI (Copied from worker_yolov3.py configuration)
    parser.add_argument('--mbbox_output', type=str, default="hasil/media/ramdisk/mbbox_frames/",
                        help='Folder location to store mbbox_frames')
    parser.add_argument('--normal_output', type=str, default="hasil/media/ramdisk/output/",
                        help='Folder location to store original_frames')

    parser.add_argument('--half', action='store_true', help='half precision FP16 inference')
    # parser.add_argument("--img_size", type=int, default=416, help="size of each image dimension")
    parser.add_argument("--img_size", type=int, default=832, help="size of each image dimension")

    # parser.add_argument("--source_type", type=str, default="folder", help="source type")
    parser.add_argument("--source_type", type=str, default="streaming", help="source type")

    # parser.add_argument("--source", type=str, default="data/5g-dive/57-frames/", help="source")
    parser.add_argument("--source", type=str, default="data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4", help="source")
    # parser.add_argument("--source", type=str, default="http://140.113.86.92:10000/drone-3.flv", help="source")
    # parser.add_argument("--source", type=str, default="http://140.113.86.92:10000/drone-2.flv", help="source")
    # parser.add_argument("--source", type=str, default="http://140.113.86.92:10000/drone-1.flv", help="source")
    # parser.add_argument("--source", type=str, default="http://192.168.0.50:10000/drone-1.flv", help="source")
    # parser.add_argument("--source", type=str, default="http://192.168.42.1/live", help="source")
    opt = parser.parse_args()
    print(opt)

    VideoStreamer(opt).run()
