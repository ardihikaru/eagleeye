import asab
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from ext_lib.utils import get_current_time

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

        self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

    # async def store_latency_data(self, latency_data):
    def _store_latency_data(self, latency_data):
        # sending get request and saving the response as response object
        req = requests.post(url=self.node_api_uri, json=latency_data, headers=self.headers)

        # extracting data in json format
        resp = req.json()

        # TODO: To store into ElasticSearchDB

        if "status" in resp and resp["status"] != 200:
            return False

        return True

    async def store_latency_data_thread(self, latency_data):
        try:
            kwargs = {
                "latency_data": latency_data
            }
            self.executor.submit(self._store_latency_data, **kwargs)
        except:
            print("\n[%s] Somehow we unable to Store latency data." % get_current_time())
            return False

        return True
