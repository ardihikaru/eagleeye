"""
    List of routes for /api/auth* endpoints
"""

from aiohttp_route_decorator import RouteCollector
import aiohttp
from ews.controllers.user.user import User as DataController
from ext_lib.utils import get_unprocessable_request

route = RouteCollector()


@route('/login', methods=['POST', 'OPTIONS'])
async def auth_login(request):
    """
        Endpoint to login into the system
        Try: curl http://localhost:8080/api/auth/login -X POST -H "Content-Type: application/json" -d '{"username":"ardi", "password": "ardi"}'
    """

    try:
        if request.method == 'POST':
            json_data = await request.json()
            resp = DataController().validate_user(json_data)
            return aiohttp.web.json_response(resp)
    except Exception as e:
        return get_unprocessable_request()


@route('/logout', methods=['GET'])
async def auth_logout(request):
    """
        Endpoint to logout into the system
        Try: curl http://localhost:8080/api/auth/login -X POST -H "Content-Type: application/json" -d '{"username":"ardi", "password": "ardi"}'
    """

    access_token = None
    try:
        access_token = (request.headers['authorization']).replace("Bearer ", "")
        access_token = access_token.encode()
    except:
        pass
    resp = DataController().do_logout(access_token)

    return aiohttp.web.json_response(resp)
