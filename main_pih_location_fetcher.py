import argparse
from libs.components.pih_location_fetcher_handler import PIHLocationFetcherHandler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')

    parser.add_argument('--pih_location_fetcher_port', type=int, default=5571, help='ZMQ Viewer port')
    parser.add_argument('--viewer_port', type=int, default=5581, help='ZMQ Viewer port')

    parser.add_argument('--plot_bbox', type=bool, default=True, help='Plot BBox (YOLOv3 Output)')
    parser.add_argument('--plot_mbbox', type=bool, default=True, help='Plot BBox (MOD Output)')

    # parser.add_argument('--viewer_all_bbox', type=bool, default=True, help='Viewer results both from YOLOv3 and MOD')
    # parser.add_argument('--viewer_all_bbox', type=bool, default=False, help='Viewer results both from YOLOv3 and MOD')

    # parser.add_argument("--enable_mbbox", type=bool, default=True,
    #                     help="Enable/disable Output MB-Box-based video streaming")
    # parser.add_argument("--enable_mbbox", type=bool, default=False,
    #                   help="Enable/disable Output MB-Box-based video streaming")
    # parser.add_argument("--default_detection", type=bool, default=True,
    #                     help="Enable/disable Output YOLOv3-based video streaming")

    opt = parser.parse_args()
    print(opt)

    plf_handler = PIHLocationFetcherHandler(opt)
    plf_handler.run()
