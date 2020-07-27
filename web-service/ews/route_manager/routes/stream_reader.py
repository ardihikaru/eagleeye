"""
    List of routes for /api/stream* endpoints
"""

from aiohttp_route_decorator import RouteCollector
import aiohttp
from ews.controllers.stream_dear.stream_reader import StreamReader as DataController
from ext_lib.utils import get_unprocessable_request

route = RouteCollector()


@route('', methods=['POST', 'OPTIONS'])
async def stream_raw(request):
    """
        Endpoint to start streaming
        Try: curl http://localhost:8080/api/auth/login -X POST -H "Content-Type: application/json" -d '{"username":"ardi", "password": "ardi"}'
    """
    # uri = request.match_info.get('uri', "Anonymous")

    try:
        if request.method == 'POST':
            request_json = await request.json()
            resp = DataController().read(request_json)
            return aiohttp.web.json_response(resp)
    except Exception as e:
        return get_unprocessable_request()
        # return aiohttp.web.HTTPBadRequest()
