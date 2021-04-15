import asab
import logging
from .v1.pv_v1 import PVv1

###

L = logging.getLogger(__name__)


###


class AlgorithmService(asab.Service):
    """ A class to validate the merged object detection and denote it either as a valid or invalid PiH Objects """

    def __init__(self, app, service_name="pv.AlgorithmService"):
        super().__init__(app, service_name)
        self.pv = PVv1()

    async def validate_mbbox(self, frame_id, total_pih_candidates, period_pih_candidates):
        self.pv.initialize(frame_id, total_pih_candidates, period_pih_candidates)
        self.pv.run()
        return self.pv.get_label(), self.pv.get_det_status()
