import argparse
from libs.addons.gps_collector.gps_model import GPSModel
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    opt = parser.parse_args()
    print(opt)

    gps_agent = GPSModel(opt)

    # Simulate GPS Data Collector
    while True:
        dummy_data = gps_agent.get_dummy_data()
        gps_agent.store_gps_data(dummy_data)
        print(" . . . Sleep for 1 second . . . ")
        time.sleep(1)  # interval 1 second
        print()
