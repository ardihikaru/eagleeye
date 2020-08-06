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
            Try: curl http://localhost:8080/api/plot -X POST -H "Content-Type: application/json"
                    -d '{
                            "category": "Object Detection",
                            "algorithm": "YOLOv3",
                            "section": "Pre-processing",
                            "latency": 24.785909,
                            "timestamp": 1596609696.1005852
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
