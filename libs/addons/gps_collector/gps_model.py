from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_set, redis_get
import time
import simplejson as json


class GPSModel(MyRedis):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        self.gps_id = 1

    def get_dummy_data(self):
        gps_data = {
            "id": self.gps_id,
            "timestamp": time.time(),
            "gps": {
                "long": 111.99,
                "lat": 188.55,
                "alt": 41.22
            }
        }
        self.gps_id += 1
        return gps_data

    def store_gps_data(self, gps_data):
        key = "gps-data-" + str(self.opt.drone_id)
        p_gps_data = json.dumps(gps_data)
        redis_set(self.rc_gps, key, p_gps_data)

        print("Stored GPS Data:", redis_get(self.rc_gps, key))
