import asab
import time
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

    def __init__(self, app, service_name="eagleeye.LatencyCollectorService"):
        super().__init__(app, service_name)

        # Get latency collection detail
        self.node_api_uri = asab.Config["eagleeye:api"]["latency"]
        self.headers = {"Content-Type": "application/json"}

        self.executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

    async def build_and_save_latency_info(self, frame_id, latency, algorithm="[?]", section="[?]", cat="sorting",
                                          node_id="-", node_name="-"):
        t0_lat = time.time()

        # build latency obj
        latency_obj = {
            "frame_id": frame_id,
            "category": cat,
            "algorithm": algorithm,
            "section": section,
            "latency": latency,
            "node_id": node_id,
            "node_name": node_name
        }

        # Submit and store latency data
        if not await self.store_latency_data_thread(latency_obj):
            L.error("[SAVE_LATENCY] Saving latency failed.")

        t1_lat = (time.time() - t0_lat) * 1000
        L.warning('[%s] Proc. Latency of %s (%.3f ms)' % (get_current_time(), section, t1_lat))

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

    def sync_store_latency_data_thread(self, latency_data):
        try:
            kwargs = {
                "latency_data": latency_data
            }
            self.executor.submit(self._store_latency_data, **kwargs)
        except:
            print("\n[%s] Somehow we unable to Store latency data." % get_current_time())
            return False

        return True
