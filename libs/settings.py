class CommonSettings:
    __shared_state = {
            "plf_config": {
                # "waiting_limit": 33.4  # in ms --> for 30 fps video
                "waiting_limit": 50  # in ms
            },
            "streaming_config": {
                "delay_disconnected": 3
            },
            "persistence_detection": {
                # "persistence_window": 3,
                # "persistence_window": 150,  # 30*5 = 150 (5 seconds)
                "persistence_window": 10,
                "tolerance_limit_percentage": 0.3  # percentage; e.g. 0.3 = 30%
            },
            "bbox_config": {
                # "pih_label_cand": "PiH Candidate",
                "pih_label_cand": "FALSE PiH",
                "pih_label": "PiH",
                "pih_color": [198, 50, 13]  # PiH bbox color: Blue
            },
            "redis_config": {
                "hostname": "localhost",
                "port": 6379,
                "password": "bismillah",
                "db": 0,
                "db_data": 1,
                "db_gps": 2,
                "db_latency": 3,
                "db_bbox": 4,
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
