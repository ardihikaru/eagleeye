
class RealtimeViewer:
    def __init__(self, drone_id):
        self.drone_id = drone_id
        self.fid = 1
        self.start_fetching = False

    def get_next_frame(self):
        if not self.start_fetching:
            self.start_fetching = True
            self.fid += 1
