import argparse
from libs.components.pih_location_fetcher_handler import PIHLocationFetcherHandler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pih_location_fetcher_port', type=int, default=5571, help='ZMQ Viewer port')
    parser.add_argument('--visualizer_port_prefix', type=str, default="558", help='ZMQ Visualizer port')  # +drone_id
    parser.add_argument('--enable_cv_out', type=bool, default=True, help='Enable/Disable Send result into Visualizer')

    parser.add_argument('--host', type=str, default="http://localhost", help='Server Host IP')
    parser.add_argument('--port', type=str, default="33000", help='Server Host Port')
    parser.add_argument('--endpoint', type=str, default="FlySocketWCF", help='Server Host End point')

    parser.add_argument('--total_drones', type=int, default=1, help='Total number of drones')

    opt = parser.parse_args()
    # print(opt)

    plf_handler = PIHLocationFetcherHandler(opt)
    plf_handler.run()
