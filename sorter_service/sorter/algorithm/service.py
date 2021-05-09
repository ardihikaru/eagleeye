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
        self.sorter = Sorter()

    async def sort_frame_sequences(self, unsorted_frame_seqs):
        self.sorter.initialize(unsorted_frame_seqs)
        self.cs.run()

        return sorted_frame_seqs
