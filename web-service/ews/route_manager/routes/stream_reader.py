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


@route('/live', methods=['GET', 'POST', 'OPTIONS'])
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
    try:
        if request.method == 'POST':
            request_json = await request.json()
            return DataController().read(request_json)
            # return aiohttp.web.json_response(DataController().read(request_json))

        if request.method == 'GET':
            return await DataController().get_data()
    except Exception as e:
        # Log the error
        L.error("Invalid request: {}".format(e))
        return aiohttp.web.HTTPBadRequest()


@route('/live/{_id}', methods=['GET', 'DELETE', 'PUT'])
async def index_by(request):
    """
        Endpoint to:
         1. GET live video stream by id
            Try: curl http://localhost:8080/api/stream/live/{_id}
         2. DELETE live video stream by id
            Try: curl http://localhost:8080/api/stream/live/{_id} -X DELETE
         3. PUT (Edit) live video stream by id
            Try: curl http://localhost:8080/api/stream/live/{_id}
                    -X POST -H "Content-Type: application/json" -d '{"algorithm":"YOLOv3"}'
    """


    try:
        _id = str(request.match_info['_id'])
        if _id is None:
            _id = str(request.match_info['id'])
    except:
        return get_unprocessable_request()

    if request.method == 'GET':
        resp = DataController().get_data_by_id(_id)
        return aiohttp.web.json_response(resp)
    elif request.method == 'DELETE':
        resp = DataController().delete_data_by_id_one(_id)
        return aiohttp.web.json_response(resp)
    elif request.method == 'PUT':
        try:
            json_data = await request.json()
            resp = DataController().update_data_by_id(_id, json_data)
            return aiohttp.web.json_response(resp)
        except:
            return get_unprocessable_request()
    else:
        return get_unprocessable_request()


# @route('/live/{_id}', methods=['POST', 'OPTIONS'])
# async def get_stream_data(request):
#     """
#         Endpoint to start streaming
#         Try: curl http://localhost:8080/api/stream/live -X POST -H "Content-Type: application/json"
#                 -d '{
#                         "raw": false,
#                         "algorithm": "YOLOv3",
#                         "uri": "rtmp://140.113.86.98:15500/live/demo",
#                         "exec": true,
#                         "worker": 1
#                     }'
#     """
#     _id = request.match_info.get('_id', "Anonymous")
#
#     try:
#         if request.method == 'GET':
#             return DataController().get_data_by(_id)
#             # return aiohttp.web.json_response(DataController().read(request_json))
#     except Exception as e:
#         # Log the error
#         L.error("Invalid request: {}".format(e))
#         return aiohttp.web.HTTPBadRequest()


# @route('/folder', methods=['POST', 'OPTIONS'])
# async def stream_folder(request):
#     """
#         Endpoint to start streaming
#         Try: curl http://localhost:8080/api/stream/live -X POST -H "Content-Type: application/json"
#                 -d '{
#                         "raw": false,
#                         "algorithm": "YOLOv3",
#                         "uri": "common_files/5g-dive/57-frames",
#                         "exec": true,
#                         "worker": 1
#                     }'
#     """
#     # uri = request.match_info.get('uri', "Anonymous")
#
#     try:
#         if request.method == 'POST':
#             request_json = await request.json()
#             resp = DataController().read(request_json)
#             return aiohttp.web.json_response(resp)
#     except Exception as e:
#         return get_unprocessable_request()
#         # return aiohttp.web.HTTPBadRequest()
