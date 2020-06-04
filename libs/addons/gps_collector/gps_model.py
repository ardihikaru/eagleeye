from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_set, redis_get
import time
from datetime import datetime
import simplejson as json
from suds.client import Client


class GPSModel(MyRedis):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        self.gps_id = 1

        self.dummy_long = 111.99
        self.dummy_lat = 188.55
        self.dummy_alt = 41.22

    def get_data(self):
        if self.opt.dummy_data:
            return self.get_dummy_data()
        else:
            return self.get_real_data()

    def get_real_data(self):
        s_url = self.opt.host + ":" + self.opt.port + "/" + self.opt.endpoint
        client = Client(s_url)
        all_drone_state = json.loads(client.service.GetAllDroneState())
        self.gps_id += 1
        return all_drone_state

    def get_dummy_data(self):
        self.dummy_long += 1
        self.dummy_lat += 1
        self.dummy_alt += 1

        gps_data = {
            "drone_id": self.opt.drone_id,
            "id": self.gps_id,
            "timestamp": time.time(),

            "drone_timestamp": time.time(),
            "Heading": "360",
            "GroundSpeed": "-0.0084148002788424",
            "Pitch": "-0.00841480027884245",
            "Roll": "-0.0021843130234628916",
            "Yaw": "2.517401695251465",

            "gps": {
                "long": self.dummy_long,
                "lat": self.dummy_lat,
                "alt": self.dummy_alt
            }
        }
        self.gps_id += 1
        return gps_data

    def printing_drone_gps(self, drone_id, long, lat, alt, t0):
        t_elapsed = (time.time() - t0) * 1000
        ts = datetime.now().strftime("%H:%M:%S")
        print("[%s] Drone-%d GPS Data (Long=%s; Lat=%s; Alt=%s); %.0fms" %
              (ts, int(drone_id), str(long), str(lat), str(alt), t_elapsed))

    def store_gps_data(self, gps_data, t0):
        if self.opt.dummy_data:
            key = "gps-data-" + str(self.opt.drone_id)
            p_gps_data = json.dumps(gps_data)
            redis_set(self.rc_gps, key, p_gps_data)

            self.printing_drone_gps(self.opt.drone_id, gps_data["gps"]["long"], gps_data["gps"]["lat"],
                                    gps_data["gps"]["alt"], t0)
        else:
            drone_id = 0
            for data in gps_data:
                key = "gps-data-" + str(drone_id)

                this_gps_data = {
                    "drone_id": data["FlyNo"],
                    "id": self.gps_id,
                    "timestamp": time.time(),

                    "drone_timestamp": data["Timestamp"],
                    "Heading": data["Heading"],
                    "GroundSpeed": data["GroundSpeed"],
                    "Pitch": data["Pitch"],
                    "Roll": data["Roll"],
                    "Yaw": data["Yaw"],

                    "gps": {
                        "long": data["Longitude"],
                        "lat": data["Latitude"],
                        "alt": data["Altitude"]
                    }
                }

                p_gps_data = json.dumps(this_gps_data)
                redis_set(self.rc_gps, key, p_gps_data)
                self.printing_drone_gps(data["FlyNo"], data["Longitude"], data["Latitude"], data["Altitude"], t0)
