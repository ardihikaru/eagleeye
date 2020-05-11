import argparse
from libs.addons.streamer.visualizer import Visualizer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument('--visualizer_port_prefix', type=str, default="558", help='ZMQ Visualizer port')  # +drone_id

    parser.add_argument('--window_width', type=int, default=1440, help='CV Window width size')
    parser.add_argument('--window_height', type=int, default=900, help='CV Window height size')
    parser.add_argument('--wait_key', type=int, default=1, help='Wait key for the screen')

    opt = parser.parse_args()
    print(opt)

    visualizer = Visualizer(opt)
    visualizer.run()