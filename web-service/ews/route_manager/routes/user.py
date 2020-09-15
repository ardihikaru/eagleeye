"""
    List of routes for /api/users* endpoints
"""

from aiohttp_route_decorator import RouteCollector
import aiohttp
from ews.controllers.user.user import User as DataController
from ext_lib.utils import get_unprocessable_request

route = RouteCollector()


@route('', methods=['POST', 'GET', 'PUT', 'DELETE'])
async def index(request):
    """
        Endpoint to:
         1. POST new user data
            Try: curl http://localhost:8080/api/users -X POST -H "Content-Type: application/json"
                    -d '{
                            "name": "Muhammad Febrian Ardiansyah",
                            "username": "ardihikaru",
                            "email": "ardihikaru3@gmail.com",
                            "password": "ardipasswd",
                            "password_confirm": "ardipasswd"
                    }'
         1. GET all user data
            Try: curl http://localhost:8080/api/users

         2. DELETE a specific user data (single ID)
            Try: curl http://localhost:8080/api/users -X DELETE -H "Content-Type: application/json"
                    -d '{
                            "id": {String}
                    }'

         3. DELETE list of user data (multiple IDs)
            Try: curl http://localhost:8080/api/users -X DELETE -H "Content-Type: application/json"
                    -d '{
                            "id": [{String}, {String}]
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
        resp = DataController().get_users(params)
        return aiohttp.web.json_response(resp)

    if request.method == 'DELETE':
        try:
            json_data = await request.json()
            resp = DataController().delete_data_by_id(json_data)
        except:
            return get_unprocessable_request()

        return aiohttp.web.json_response(resp)


@route('/{_id}', methods=['GET', 'DELETE', 'PUT'])
async def index_by(request):
    """
        Endpoint to:
         1. GET user data by id
            Try: curl http://localhost:8080/api/users/{_id}
         2. DELETE user data by id
            Try: curl http://localhost:8080/api/users/{_id} -X DELETE
         3. PUT (Edit) user data by id
            Try: curl http://localhost:8080/api/users/{_id}
                    -X POST -H "Content-Type: application/json" -d '{"name":"Kucing"}'
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
