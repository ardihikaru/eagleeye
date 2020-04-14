from libs.settings import common_settings

class BehaviorDetection:
    def __init__(self, opt, frame_id, detected_mbbox):
        self.opt = opt
        self.frame_id = frame_id
        self.detected_mbbox = detected_mbbox

    def run(self):
        pass