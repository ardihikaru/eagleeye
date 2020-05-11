from imutils.video import FPS
import datetime


class MyFPS(FPS):
    def __init__(self):
        super().__init__()

    def num_frames(self):
        return self._numFrames

    def current_elapsed(self):
        cur_ts = datetime.datetime.now()
        time_elapsed = (cur_ts - self._start).total_seconds()
        # print(" ## time_elapsed:", time_elapsed)
        return time_elapsed

    def current_fps(self):
        # print(" -- self._numFrames:", self._numFrames)
        # print(" -- self.elapsed:", self.current_elapsed)
        return self._numFrames / self.current_elapsed()
