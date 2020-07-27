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
