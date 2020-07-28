class Config:
    __shared_state = {
            "bbox_config": {
                "default_label": "Unknown",
                "default_color": [198, 50, 13],  # Default bbox color: Blue
            },
        }

    def __init__(self):
        self.__dict__ = self.__shared_state

    def extract(self):
        return self.__shared_state


config = Config().extract()

