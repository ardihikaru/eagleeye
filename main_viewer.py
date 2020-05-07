import argparse
from libs.addons.streamer.viewer import Viewer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument('--viewer_port', type=int, default=5571, help='ZMQ Viewer port')

    # parser.add_argument("--enable_cv_out", type=bool, default=False, help="Enable/disable Output video streaming")
    parser.add_argument("--enable_cv_out", type=bool, default=True, help="Enable/disable Output video streaming")
    parser.add_argument('--viewer_version', type=int, default=2,
                        help='Viewer version to show real-time image processing')
    parser.add_argument('--viewer_width', type=int, default=1366, help='Viewer width size')
    parser.add_argument('--viewer_height', type=int, default=768, help='Viewer height size')
    parser.add_argument('--viewer_all_bbox', type=bool, default=True, help='Viewer results both from YOLOv3 and MOD')
    # parser.add_argument('--viewer_all_bbox', type=bool, default=False, help='Viewer results both from YOLOv3 and MOD')

    parser.add_argument("--enable_mbbox", type=bool, default=True,
                        help="Enable/disable Output MB-Box-based video streaming")
    # parser.add_argument("--enable_mbbox", type=bool, default=False,
    #                   help="Enable/disable Output MB-Box-based video streaming")
    parser.add_argument("--default_detection", type=bool, default=True,
                        help="Enable/disable Output YOLOv3-based video streaming")

    opt = parser.parse_args()
    print(opt)

    viewer = Viewer(opt)
    viewer.run()
