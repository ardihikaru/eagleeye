"""
    List of routes for /api/people* endpoints
"""

from aiohttp_route_decorator import RouteCollector
import aiohttp
from trackilo.controllers.people.people import People as DataController
from trackilo.addons.utils import get_unprocessable_request

route = RouteCollector()


@route('', methods=['POST', 'GET', 'OPTIONS'])
async def index_people(request):
    """
        Endpoint to:
         1. GET all people data
            Try: curl http://localhost:8080/api/people
         2. POST a new people data
            Try: curl http://localhost:8080/api/people -X POST -H "Content-Type: application/json"
                    -d '{
                            "name": "Ardi",
                            "SSID": "BHKJG*&OTGugB",
                            "sync_datetime": "2020-07-15 02:42:02",
                            "description": "Scrum meeting & Introduction"
                        }'
    """

    if request.method == 'POST':
        try:
            json_data = await request.json()
            resp = DataController().register(json_data)
        except:
            return get_unprocessable_request()

        return aiohttp.web.json_response(resp)

    if request.method == 'GET':
        params = request.rel_url.query
        resp = DataController().get_data(params)
        return aiohttp.web.json_response(resp)


@route('/{_id}', methods=['GET', 'DELETE', 'PUT'])
async def index_people_by(request):
    """
        Endpoint to:
         1. GET people data by id
            Try: curl http://localhost:8080/api/people/{_id}
         2. DELETE people data by id
            Try: curl http://localhost:8080/api/people/{_id} -X DELETE
         3. PUT (Edit) people data by id
            Try: curl http://localhost:8080/api/people/{_id}
                    -X POST -H "Content-Type: application/json" -d '{"name":"Yuza"}'
    """


    try:
        _id = str(request.match_info['_id'])
        if _id is None:
            _id = str(request.match_info['id'])
    except:
        return get_unprocessable_request()

    if request.method == 'GET':

        # resp = DataController().get_data_by_id(_id)
        resp = await DataController().get_data_by_id(_id)
        return aiohttp.web.json_response(resp)
    elif request.method == 'DELETE':
        resp = DataController().delete_data_by_id(_id)
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
