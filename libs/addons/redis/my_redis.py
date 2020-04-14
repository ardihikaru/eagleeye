from redis import StrictRedis
from libs.settings import common_settings

class MyRedis:
    def __init__(self):
        self.rc = StrictRedis(
            host=common_settings["redis_config"]["hostname"],
            port=common_settings["redis_config"]["port"],
            password=common_settings["redis_config"]["password"],
            db=common_settings["redis_config"]["db"],
            decode_responses=True
        )

        self.rc_gps = StrictRedis(
            host=common_settings["redis_config"]["hostname"],
            port=common_settings["redis_config"]["port"],
            password=common_settings["redis_config"]["password"],
            db=common_settings["redis_config"]["db_gps"],
            decode_responses=True
        )

        self.rc_latency = StrictRedis(
            host=common_settings["redis_config"]["hostname"],
            port=common_settings["redis_config"]["port"],
            password=common_settings["redis_config"]["password"],
            db=common_settings["redis_config"]["db_latency"],
            decode_responses=True
        )

    def get_rc(self):
        return self.rc

    def get_rc_gps(self):
        return self.rc_gps

    def get_rc_latency(self):
        return self.rc_latency

    def delete_all_keys(self):
        print(" Current Keys = ", self.rc.keys())
        for key in self.rc.keys():
            self.rc.delete(key)
        print(" New Keys = ", self.rc.keys())

        print(" Current Keys = ", self.rc_gps.keys())
        for key in self.rc_gps.keys():
            self.rc_gps.delete(key)
        print(" New Keys = ", self.rc_gps.keys())

        print(" Current Keys = ", self.rc_latency.keys())
        for key in self.rc_latency.keys():
            self.rc_latency.delete(key)
        print(" New Keys = ", self.rc_latency.keys())
