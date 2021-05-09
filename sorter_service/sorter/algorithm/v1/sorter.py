

class Sorter(object):
    def __init__(self):
        self.unsorted_frame_seqs = []
        self.sorted_frame_seqs = []

    def initialize(self, unsorted_frame_seqs):
        self.unsorted_frame_seqs = unsorted_frame_seqs
        self.sorted_frame_seqs = []  # default value

    def run(self):
        pass

    def get_sorted_frame_seqs(self):
        return self.sorted_frame_seqs
