import asab
import logging
from .handler import ReaderHandler

###

L = logging.getLogger(__name__)


###


class ReaderService(asab.Service):
    """ Video stream / tuple of images extractor """

    def __init__(self, app, service_name="scheduler.ReaderService"):
        super().__init__(app, service_name)
        self.SubscriptionHandler = ReaderHandler(app)
        self.SubscriptionHandler.ExtractorService = app.get_service('scheduler.ExtractorService')

    async def start_subscription(self):
        await self.SubscriptionHandler.set_zmq_configurations()
        await self.SubscriptionHandler.start()
