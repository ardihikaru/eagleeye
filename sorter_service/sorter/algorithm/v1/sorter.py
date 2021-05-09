from algorithm.sorting_network.sorting_network import ComparisonNetwork, Comparator
import logging

###

L = logging.getLogger(__name__)


###


class Sorter(object):
    def __init__(self, config):
        self.unsorted_frame_seq = []
        self.sorted_frame_seq = None

        self.cn_input_root_dir = config["root_dir"]
        self.cn = []
        self.cn_valid = False  # an indicator that the generated Comparison Network is valid

    def build_comparison_network(self, cn_size, cn_input_model=None):
        """ Build comparison network based on the pre-defined input model (4, 5, and 16) or based on the user's input"""
        # initialize an empty Comparison Network (CN) instance
        cn = ComparisonNetwork()

        # if `cn_data` available, use this network instead!
        # TODO: validate input `cn_input_model` from the user
        if cn_input_model is not None:
            for c in cn_input_model:
                cn.append(Comparator(c))
        else:
            # build filename
            filename = "{}/{}-input.cn".format(self.cn_input_root_dir, cn_size)

            # load CN data
            with open(filename, 'r') as f:
                for line in f:
                    for c in line.split(","):
                        cn.append(Comparator(c))

        return cn

    def initialize(self, unsorted_frame_seq, cn_size=None, cn_input_model=None):
        # convert list input into tuple
        self.unsorted_frame_seq = tuple(unsorted_frame_seq)

        try:
            # build comparison network
            self.cn = self.build_comparison_network(cn_size, cn_input_model)

            # validate CN status
            self.cn_valid = True
        except FileNotFoundError as e:
            L.error("[SORTING_NETWORK] File not found: `{}`".format(e))
        except AttributeError as e:
            L.error("[SORTING_NETWORK] Another issue occurs: `{}`".format(e))

    def run(self):
        if not self.cn_valid:
            L.error("[SORTING_NETWORK] Invalid Comparison Network size / input model")
            return False

        try:
            self.sorted_frame_seq = self.cn.sort_sequence(self.unsorted_frame_seq)
        except Exception as e:
            L.error("[SORTING_NETWORK] Sorting failed: `{}`".format(e))

    def get_sorted_frame_seq(self):
        return self.sorted_frame_seq
