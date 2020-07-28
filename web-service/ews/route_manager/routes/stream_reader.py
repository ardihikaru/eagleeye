"""
    List of routes for /api/stream* endpoints
"""

from aiohttp_route_decorator import RouteCollector
import aiohttp
from ews.controllers.stream_reader.stream_reader import StreamReader as DataController
from ext_lib.utils import get_unprocessable_request
import logging

###

L = logging.getLogger(__name__)

###

route = RouteCollector()

#
# @route('/video_feed', methods=['GET'])
# async def stream_live(request):
#     """
#         To streaming video from the drone
#     """
#     # uri = request.match_info.get('uri', "Anonymous")
#
#     try:
#         request_json = await request.json()
#         return DataController().video_feed(request_json)
#     except Exception as e:
#         # Log the error
#         L.error("Invalid request: {}".format(e))
#         return aiohttp.web.HTTPBadRequest()


@route('/live', methods=['POST', 'OPTIONS'])
async def stream_live(request):
    """
        Endpoint to start streaming
        Try: curl http://localhost:8080/api/stream/live -X POST -H "Content-Type: application/json"
                -d '{
                        "raw": false,
                        "algorithm": "YOLOv3",
                        "uri": "rtmp://140.113.86.98:15500/live/demo",
                        "exec": true,
                        "worker": 1
                    }'
    """
    # uri = request.match_info.get('uri', "Anonymous")

    try:
        if request.method == 'POST':
            request_json = await request.json()
            return DataController().read(request_json)
    except Exception as e:
        # Log the error
        L.error("Invalid request: {}".format(e))
        return aiohttp.web.HTTPBadRequest()


@route('/folder', methods=['POST', 'OPTIONS'])
async def stream_folder(request):
    """
        Endpoint to start streaming
        Try: curl http://localhost:8080/api/stream/live -X POST -H "Content-Type: application/json"
                -d '{
                        "raw": false,
                        "algorithm": "YOLOv3",
                        "uri": "common_files/5g-dive/57-frames",
                        "exec": true,
                        "worker": 1
                    }'
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
