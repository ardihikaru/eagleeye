import asab
import logging

###

L = logging.getLogger(__name__)

###

pcs = set()


class WebRealtimeHandler(object):
    """
        Web Realtime Handler
    """

    def __init__(self, app):
        self.EWSService = app.get_service("ews.service")
        self.AIORTCService = app.get_service("ews.aio-rtc-service")

        web_svc = app.get_service("asab.WebService")
        self.ServiceAPIWebContainer = asab.web.WebContainer(web_svc, 'eagleeye:realtime')

        # aioRTC
        self.ServiceAPIWebContainer.WebApp.on_shutdown.append(self.AIORTCService.on_shutdown)
        self.ServiceAPIWebContainer.WebApp.router.add_get("/", self.AIORTCService.index)
        self.ServiceAPIWebContainer.WebApp.router.add_get("/client.js", self.AIORTCService.javascript)
        self.ServiceAPIWebContainer.WebApp.router.add_post("/offer", self.AIORTCService.offer)
