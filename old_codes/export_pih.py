import argparse
from libs.addons.redis.data_exporter import DataExporter

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument('--export_path', type=str, default="data/5g-dive/pih_coords.json", help='Export path')
    opt = parser.parse_args()
    print(opt)

    redis_data = DataExporter(opt)
    redis_data.export_pih_coord()
