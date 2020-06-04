import argparse
from libs.addons.gps_collector.gps_model import GPSModel
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument('--host', type=str, default="http://localhost", help='Server Host IP')
    parser.add_argument('--port', type=str, default="33000", help='Server Host Port')
    parser.add_argument('--endpoint', type=str, default="FlySocketWCF", help='Server Host End point')

    parser.add_argument('--no-dummy', dest='dummy_data', action='store_false', help="Use real data")
    parser.set_defaults(small=True)

    opt = parser.parse_args()
    print(opt)

    gps_agent = GPSModel(opt)

    # Execute GPS Data Collector
    while True:
        t0 = time.time()
        gps_data = gps_agent.get_data()
        gps_agent.store_gps_data(gps_data, t0)
        # time.sleep(1)  # interval 1 second
        print()
