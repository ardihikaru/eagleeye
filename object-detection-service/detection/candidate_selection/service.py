import asab
import logging
from detection.candidate_selection.cs_v1 import CSv1
from detection.candidate_selection.cs_v2 import CSv2

###

L = logging.getLogger(__name__)


###


class CandidateSelectionService(asab.Service):
    """ A class to calculate the merged object detection """

    def __init__(self, app, service_name="detection.CandidateSelectionService"):
        super().__init__(app, service_name)
        self.cs = CSv2()

    async def calc_mbbox(self, bbox_data):
        return self.cs.get_mbbox(bbox_data)
