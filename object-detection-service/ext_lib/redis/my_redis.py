"""
   This class initiate RedisDB connection;
   Every Controller class will inherit this class as the base
"""

from redis import StrictRedis


class MyRedis:
    def __init__(self, config):
        self.rc = StrictRedis(
            host=config["redis"]["hostname"],
            port=config["redis"]["port"],
            password=config["redis"]["password"],
            db=config["redis"]["db"],
            decode_responses=True
        )

    def get_rc(self):
        return self.rc

    def delete_by_client(self, rci):
        # print(" Current Keys = ", rci.keys())
        for key in rci.keys():
            rci.delete(key)
        # print(" New Keys = ", rci.keys())

    def delete_all_keys(self):
        self.delete_by_client(self.rc)
