import asab
import logging
from detection.candidate_selection.cs_v1.cs_v1 import CSv1  # TODO: Not yet re-implemented!
from detection.candidate_selection.cs_v2.cs_v2 import CSv2

###

L = logging.getLogger(__name__)


###


class CandidateSelectionService(asab.Service):
    """ A class to calculate the merged object detection """

    def __init__(self, app, service_name="detection.CandidateSelectionService"):
        super().__init__(app, service_name)
        self.cs = CSv2()

    async def calc_mbbox(self, bbox_data, det, names, h, w, c, selected_pairs):
        self.cs.initialize(det, names, h, w, c, selected_pairs, bbox_data)
        self.cs.run()
        return self.cs.get_detected_mbbox(), self.cs.get_selected_pairs()
