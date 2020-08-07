"""
    List of routes for /api/plot* endpoints
"""

from aiohttp_route_decorator import RouteCollector
import aiohttp
from ews.controllers.plot.plot import Plot as DataController
import logging

###

L = logging.getLogger(__name__)

###

route = RouteCollector()


@route('/latency/detection', methods=['POST'])
async def plot(request):
    """
        Endpoint to:
         1. POST new plot
            Try: curl http://localhost:8080/api/plot/latency/detection -X POST -H "Content-Type: application/json"
                    -d '{
                            "name": ["preproc_det", "detection", "candidate_selection"],
                            "section": ["preproc_det", "detection", "candidate_selection"]
                        }'
    """

    if request.method == 'POST':
        try:
            json_data = await request.json()
            resp = DataController().plot_det_latency(json_data)
        except Exception as e:
            # return get_unprocessable_request()
            # Log the error
            L.error("Invalid request: {}".format(e))
            return aiohttp.web.HTTPBadRequest()

        return aiohttp.web.json_response(resp)

@route('/latency/detection/csv', methods=['POST'])
async def plot(request):
    """
        Endpoint to:
         1. POST new plot
            Try: curl http://localhost:8080/api/plot/latency/detection/csv -X POST -H "Content-Type: application/json"
                    -d '{
                            "name": "worker=1"
                            "section": ["e2e_latency"]
                        }'
    """

    if request.method == 'POST':
        try:
            json_data = await request.json()
            resp = DataController().export_det_latency(json_data)
        except Exception as e:
            # return get_unprocessable_request()
            # Log the error
            L.error("Invalid request: {}".format(e))
            return aiohttp.web.HTTPBadRequest()

        return aiohttp.web.json_response(resp)

@route('/latency/nodes', methods=['POST'])
async def plot(request):
    """
        Endpoint to:
         1. GET node latency comparison plot
            Try: curl http://localhost:8080/api/plot/latency/nodes -X POST -H "Content-Type: application/json"
                    -d '{
                            "node_info": [
                                {
                                    "path": "/home/ardi516/devel/nctu/eagleeye/output/csv/2020-08-07_15:58:51/e2e_latency_worker=1_n=40.csv",
                                    "num_node": 1
                                },
                                {
                                    "path": "/home/ardi516/devel/nctu/eagleeye/output/csv/2020-08-07_15:58:51/e2e_latency_worker=3_n=40.csv",
                                    "num_node": 3
                                },
                                {
                                    "path": "/home/ardi516/devel/nctu/eagleeye/output/csv/2020-08-07_15:58:51/e2e_latency_worker=6_n=40.csv",
                                    "num_node": 6
                                }
                            ],
                            "batch_size": 6,
                            "max_data": 36
                        }'
    """

    if request.method == 'POST':
        try:
            json_data = await request.json()
            resp = DataController().plot_node_latency(json_data)
        except Exception as e:
            # return get_unprocessable_request()
            # Log the error
            L.error("Invalid request: {}".format(e))
            return aiohttp.web.HTTPBadRequest()

        return aiohttp.web.json_response(resp)
