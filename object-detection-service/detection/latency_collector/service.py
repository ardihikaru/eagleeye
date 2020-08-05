import asab
import logging
import time
import requests

###

L = logging.getLogger(__name__)


###


class LatencyCollectorService(asab.Service):
    """
        A class to store latency data into MongoDB
    """

    def __init__(self, app, service_name="detection.LatencyCollectorService"):
        super().__init__(app, service_name)

        # Get latency collection detail
        self.node_api_uri = asab.Config["eagleeye:api"]["latency"]
        self.headers = {"Content-Type": "application/json"}

    async def store_latency_data(self, latency_data):
        print("#### I am store_latency_data function from ResizerService!")
        
        # sending get request and saving the response as response object
        req = requests.post(url=self.node_api_uri, json=latency_data, headers=self.headers)

        # extracting data in json format
        resp = req.json()

        if "status" in resp and resp["status"] != 200:
            await self.SubscriptionHandler.stop()

        return True
