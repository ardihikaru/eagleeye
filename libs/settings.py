class CommonSettings:
    __shared_state = {
            "redis_config": {
                "hostname": "localhost",
                "port": 6379,
                "password": "bismillah",
                "db": 0,
                "db_data": 1,
                "db_gps": 2,
                "db_latency": 3,
                "channel_prefix": "stream_",
                "heartbeat": {
                    "cpu": 1,
                    "gpu": 0.0
                    # "gpu": 0.005
                }
            },
            "drone_info":{
                "fps": 30
            },
            "system_printing": True,
            "log_path": "/app/resources/logs"
        }
    def __init__(self):
        self.__dict__ = self.__shared_state

    def extract(self):
        return self.__shared_state

common_settings  = CommonSettings().extract()
