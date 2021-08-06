import asab
import logging
from .cs_v1.cs_v1 import CSv1  # TODO: Not yet re-implemented!
from .cs_v2.cs_v2 import CSv2

###

L = logging.getLogger(__name__)


###


class CandidateSelectionService(asab.Service):
    """ A class to calculate the merged object detection """

    def __init__(self, app, service_name="pcs.CandidateSelectionService"):
        super().__init__(app, service_name)
        self.cs = CSv2()

    # async def calc_mbbox(self, det, names, h, w, c, selected_pairs):
    async def calc_mbbox(self, det, names, h, w, c):
        self.cs.initialize(det, names, h, w, c)
        self.cs.run()
        return self.cs.get_detected_mbbox()
