import asab
import logging
from detection.persistence_validation.pv_v1 import PVv1
from detection.persistence_validation.pv_v2 import PVv2  # TODO: To make optimized version @TIM

###

L = logging.getLogger(__name__)


###


class PersistenceValidationService(asab.Service):
    """ A class to calculate the merged object detection """

    def __init__(self, app, service_name="detection.PersistenceValidationService"):
        super().__init__(app, service_name)
        self.pv = PVv1()

    async def predict_mbbox(self, mbbox_data):
        return self.pv.get_mbbox_pv(mbbox_data)
