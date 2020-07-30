import asab
import logging
from .handler import CSSv1Handler

###

L = logging.getLogger(__name__)


###


class CSSv1Service(asab.Service):
    """
        PiH Candidate Selection algorithm version 1.0
    """

    def __init__(self, app, service_name="css.CSSv1Service"):
        super().__init__(app, service_name)
        self.app = app
        self.SubscriptionHandler = CSSv1Handler(app)

    async def start_subscription(self):
        await self.SubscriptionHandler.set_configuration()
        await self.SubscriptionHandler.start()
