import asab
import logging
from .v1.sorter import Sorter

###

L = logging.getLogger(__name__)


###


class AlgorithmService(asab.Service):
    """
        A class to perform Sorter algorithm to sort frame sequences in which they are collected in an unsorted manner
    """

    def __init__(self, app, service_name="sorter.AlgorithmService"):
        super().__init__(app, service_name)
        self.sorter = Sorter(asab.Config["strategy"])
        self.cn_size = asab.Config["strategy"].getint("max_pool")

    async def sort_frame_sequences(self, unsorted_frame_seqs):
        # initialize and run sortet network with the input
        self.sorter.initialize(unsorted_frame_seqs, cn_size=self.cn_size)
        self.sorter.run()

        # collect sorted data
        sorted_frame_seq = self.sorter.get_sorted_frame_seq()

        return sorted_frame_seq
