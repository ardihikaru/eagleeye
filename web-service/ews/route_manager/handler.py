import asyncio
import asab
import logging
from ews.route_manager.routes import auth as route_auth
from ews.route_manager.routes import user as route_user
from ews.route_manager.routes import stream_reader as route_stream_reader
from ews.route_manager.routes import node as route_node
from ews.route_manager.routes import location as route_location
from ews.route_manager.routes import latency as route_latency
from ews.route_manager.routes import plot as route_plot
from aiohttp_jwt import JWTMiddleware
from ext_lib.database_blacklist.blacklist_helpers import is_token_revoked
from ext_lib.redis.my_redis import MyRedis
from aiohttp_middlewares import (
    cors_middleware,
    error_middleware,
)


###

L = logging.getLogger(__name__)


###


class RouteWebHandler(object):
    """
        Route Manager
    """

    # def __init__(self, app, service_name="ews.service"):
    def __init__(self, app):
        # super().__init__(app, service_name)
        # super().__init__(app)

        self.EWSService = app.get_service("ews.service")
        # self.AIORTCService = app.get_service("ews.aio-rtc-service")

        web_svc = app.get_service("asab.WebService")
        self.ServiceAPIWebContainer = asab.web.WebContainer(web_svc, 'eagleeye:api')

        # Enable CORS to CORS middleware
        self.ServiceAPIWebContainer.WebApp.middlewares.append(cors_middleware(origins=(asab.Config["clients"]
                                                                                       ["source_ip"],)))

        route_auth.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/auth')
        route_user.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/users')
        route_stream_reader.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/stream')
        route_node.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/nodes')
        route_location.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/locations')
        route_latency.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/latency')
        route_plot.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/plot')

        # Enable exception to JSON exception middleware
        self.ServiceAPIWebContainer.WebApp.middlewares.append(asab.web.rest.JsonExceptionMiddleware)

        # Enable exception to JWT middleware
        self.ServiceAPIWebContainer.WebApp.middlewares.append(JWTMiddleware(
            secret_or_pub_key=asab.Config["jwt"]["secret_key"],
            request_property="user",
            # whitelist=[r"/api/stream*", r"/api/users*", r"/api/auth/login"],  # use this to disable access_token validation
            # whitelist=[r"/api/users*", r"/api/auth/login"],  # use this to disable access_token validation
            whitelist=[r"/api*"],  # Final code: Please enable this one instead
            # whitelist=[r"/api/auth/login"],  # Final code: Please enable this one instead
            # token_getter=self.get_token,
            token_getter=self.EWSService.get_token,
            # is_revoked=self.is_revoked,
            is_revoked=self.EWSService.is_revoked,
        ))
