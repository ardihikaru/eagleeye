import asyncio
import asab
import logging
from ews.route_manager.routes import auth as route_auth
from ews.route_manager.routes import user as route_user
from ews.route_manager.routes import stream_reader as route_stream_reader
from ews.route_manager.routes import node as route_node
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


class RouteManagerModule(asab.Service):
    """
        Route Manager
    """

    def __init__(self, app, service_name="ews.service"):
        super().__init__(app, service_name)

        web_svc = app.get_service("asab.WebService")
        self.ServiceAPIWebContainer = asab.web.WebContainer(web_svc, 'eagleeye:api')

        # Enable CORS to CORS middleware
        self.ServiceAPIWebContainer.WebApp.middlewares.append(cors_middleware(origins=(asab.Config["clients"]["source_ip"],)))

        route_auth.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/auth')
        route_user.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/users')
        route_stream_reader.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/streams')
        route_node.route.add_to_router(self.ServiceAPIWebContainer.WebApp.router, prefix='/api/nodes')

        # Enable exception to JSON exception middleware
        self.ServiceAPIWebContainer.WebApp.middlewares.append(asab.web.rest.JsonExceptionMiddleware)

        # Enable exception to JWT middleware
        self.ServiceAPIWebContainer.WebApp.middlewares.append(JWTMiddleware(
            secret_or_pub_key=asab.Config["jwt"]["secret_key"],
            request_property="user",
            whitelist=[r"/api/stream*", r"/api/users*", r"/api/auth/login"],  # use this to disable access_token validation
            # whitelist=[r"/api/users*", r"/api/auth/login"],  # use this to disable access_token validation
            # whitelist=[r"/api/auth/login"],  # Final code: Please enable this one instead
            token_getter=self.get_token,
            is_revoked=self.is_revoked,
        ))

    async def is_revoked(self, request, payload):
        """
            Verify the collected access_token, checking whether it has been blacklisted/revoked
            (due to user logout function) or not
        """

        try:
            access_token = (request.headers['authorization']).replace("Bearer ", "")

            #  check if the access token has been blacklisted or not
            if is_token_revoked(MyRedis(asab.Config).get_rc(), access_token):
                return True
        except:
            pass
        return False

    async def get_token(self, request):
        """
           Collect and control access_token; Currently it simply forward the information
        """
        access_token = None
        try:
            access_token = (request.headers['authorization']).replace("Bearer ", "")
            access_token = access_token.encode()
        except:
            pass
        return access_token
