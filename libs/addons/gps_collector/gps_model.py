from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_set, redis_get
import time
from datetime import datetime
import simplejson as json


class GPSModel(MyRedis):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        self.gps_id = 1
        self.dummy_long = 111.99
        self.dummy_lat = 188.55
        self.dummy_alt = 41.22

    def get_dummy_data(self):
        self.dummy_long += 1
        self.dummy_lat += 1
        self.dummy_alt += 1

        gps_data = {
            "drone_id": self.opt.drone_id,
            "id": self.gps_id,
            "timestamp": time.time(),
            "gps": {
                "long": self.dummy_long,
                "lat": self.dummy_lat,
                "alt": self.dummy_alt
            }
        }
        self.gps_id += 1
        return gps_data

    def store_gps_data(self, gps_data):
        key = "gps-data-" + str(self.opt.drone_id)
        p_gps_data = json.dumps(gps_data)
        redis_set(self.rc_gps, key, p_gps_data)

        long = gps_data["gps"]["long"]
        lat = gps_data["gps"]["lat"]
        alt = gps_data["gps"]["alt"]

        ts = datetime.now().strftime("%H:%M:%S")
        print("[%s] Drone-%d GPS Data (Long=%s; Lat=%s; Alt=%s)" % (ts, int(self.opt.drone_id), str(long), str(lat), str(alt)))
        # print("Captured GPS Data:", redis_get(self.rc_gps, key))
