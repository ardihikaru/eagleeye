"""
   This class initiate RedisDB connection;
   Every Controller class will inherit this class as the base
"""

from redis import StrictRedis


class MyRedis:
    def __init__(self, config):
        self._set_rc(config)

    def _set_rc(self, config):
        print(">> pass:", config["redis"]["password"])
        print(">>>LEN:", len(config["redis"]["password"]))
        if not config["redis"]["password"]:
            # has no password
            print(">>> NO PASSWORD")
            self.rc = StrictRedis(
                host=config["redis"]["hostname"],
                port=config["redis"]["port"],
                db=config["redis"]["db"],
                decode_responses=True
            )
        else:
            # has password
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
