"""
    List of routes for /api/latency* endpoints
"""

from aiohttp_route_decorator import RouteCollector
import aiohttp
from ews.controllers.latency.latency import Latency as DataController
from ext_lib.utils import get_unprocessable_request
import logging

###

L = logging.getLogger(__name__)

###

route = RouteCollector()


@route('', methods=['POST', 'GET', 'DELETE'])
async def latency(request):
    """
        Endpoint to:
         1. POST new latency
            Try: curl http://localhost:8080/api/latency -X POST -H "Content-Type: application/json"
                    -d '{
                            "category": "Object Detection",
                            "algorithm": "YOLOv3",
                            "section": "Pre-processing",
                            "latency": 24.785909,
                            "timestamp": 1596609696.1005852
                    }'

                    OR
                    -d '{
                            "category": "Object Detection",
                            "algorithm": "PiH Candidate Selection",
                            "section": "PiH Candidate Selection",
                            "latency": 24.785909,
                            "timestamp": 1596609696.1005852
                    }'
         1. GET all latency
            Try: curl http://localhost:8080/api/latency

         2. DELETE a specific latency (single ID)
            Try: curl http://localhost:8080/api/latency -X DELETE -H "Content-Type: application/json"
                    -d '{
                            "id": {String}
                    }'

         3. DELETE list of latency (multiple IDs)
            Try: curl http://localhost:8080/api/latency -X DELETE -H "Content-Type: application/json"
                    -d '{
                            "id": [{String}, {String}]
                    }'
    """

    if request.method == 'POST':
        try:
            json_data = await request.json()
            resp = DataController().register(json_data)
        except Exception as e:
            # return get_unprocessable_request()
            # Log the error
            L.error("Invalid request: {}".format(e))
            return aiohttp.web.HTTPBadRequest()

        return aiohttp.web.json_response(resp)

    if request.method == 'GET':
        # params = request.rel_url.query
        resp = DataController().get_data()
        return aiohttp.web.json_response(resp)

    if request.method == 'DELETE':
        try:
            json_data = await request.json()
            resp = DataController().bulk_delete_data_by_id(json_data)
        except:
            return get_unprocessable_request()

        return aiohttp.web.json_response(resp)


@route('/{_id}', methods=['GET', 'DELETE', 'PUT'])
async def latency_by(request):
    """
        Endpoint to:
         1. GET latency by id
            Try: curl http://localhost:8080/api/latency/{_id}
         2. DELETE latency by id
            Try: curl http://localhost:8080/api/latency/{_id} -X DELETE
         3. PUT (Edit) latency by id
            Try: curl http://localhost:8080/api/latency/{_id}
                    -X POST -H "Content-Type: application/json" -d '{"category":"Category new"}'
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
