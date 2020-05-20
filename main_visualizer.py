import argparse
from libs.addons.streamer.visualizer import Visualizer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument('--visualizer_port_prefix', type=str, default="558", help='ZMQ Visualizer port')  # +drone_id

    # parser.add_argument('--window_width', type=int, default=1441, help='CV Window width size')
    # parser.add_argument('--window_height', type=int, default=901, help='CV Window height size')
    # parser.add_argument('--window_width', type=int, default=1024, help='CV Window width size')
    # parser.add_argument('--window_height', type=int, default=768, help='CV Window height size')
    parser.add_argument('--window_width', type=int, default=1680, help='CV Window width size')
    parser.add_argument('--window_height', type=int, default=1050, help='CV Window height size')
    parser.add_argument('--wait_key', type=int, default=1, help='Wait key for the screen')

    parser.add_argument('--original', dest='original', action='store_true', help='Only show original output stream')
    parser.set_defaults(original=False)

    parser.add_argument('--small', dest='small', action='store_true', help='Show 1/4 of the monitor resolution')
    parser.set_defaults(small=True)

    parser.add_argument('--no-fps', dest='show_fps', action='store_false', help="Disable FPS information")
    parser.set_defaults(small=True)

    opt = parser.parse_args()
    # print(opt)

    visualizer = Visualizer(opt)
    visualizer.run()
