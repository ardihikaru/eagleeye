import asab
import logging
from .handler import YOLOv3Handler

###

L = logging.getLogger(__name__)


###


class YOLOv3Service(asab.Service):
    """
        Object Detection algorithm based on YOLOv3
    """

    def __init__(self, app, service_name="detection.YOLOv3Service"):
        super().__init__(app, service_name)
        self.SubscriptionHandler = YOLOv3Handler(app)

    async def start_subscription(self):
        await self.SubscriptionHandler.start()
