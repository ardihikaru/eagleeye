import asab
import logging
from ext_lib.database_blacklist.blacklist_helpers import is_token_revoked
from ext_lib.redis.my_redis import MyRedis


###

L = logging.getLogger(__name__)


###


class RouteManagerService(asab.Service):
    """
        Route Manager Service
    """

    def __init__(self, app, service_name="ews.service"):
        super().__init__(app, service_name)

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
