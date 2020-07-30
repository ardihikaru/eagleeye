import asab
import logging
from .handler import CSSv2Handler

###

L = logging.getLogger(__name__)


###


class CSSv2Service(asab.Service):
    """
        PiH Candidate Selection algorithm version 2.0
    """

    def __init__(self, app, service_name="css.CSSv2Service"):
        super().__init__(app, service_name)
        self.app = app
        self.SubscriptionHandler = CSSv2Handler(app)

    async def start_subscription(self):
        await self.SubscriptionHandler.set_configuration()
        await self.SubscriptionHandler.start()
