from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.utils import get_gps_data
from libs.addons.gps_collector.gps_model import GPSModel


class GPSSender(MyRedis):
    def __init__(self, opt, drone_id):
        super().__init__()
        self.opt = opt
        self.drone_id = drone_id
        self.gps_agent = GPSModel(opt)

    def send_gps_data(self):
        gps_data = get_gps_data(self.rc_gps, self.drone_id)
        self.gps_agent.send_gps_to_drone(self.drone_id, gps_data)
