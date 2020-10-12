import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_set, redis_get
from ext_lib.utils import get_current_time, get_random_str
from concurrent.futures import ThreadPoolExecutor
import time

###

L = logging.getLogger(__name__)


###


class GPSCollectorService(asab.Service):
    """
        GPS Collector Service
    """

    def __init__(self, app, service_name="ews.GPSCollectorService"):
        super().__init__(app, service_name)
        _redis = MyRedis(asab.Config)
        self._rc = _redis.get_rc()
        self._drone_id = asab.Config["stream:config"]["drone_id"]  # TODO: DroneID should be DYNAMIC!
        self._gps_key_prefix = asab.Config["stream:config"]["gps_key_prefix"]
        self._executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))

    async def initialize(self, app):
        L.warning("\n[%s] Initializing GPS Collector Service" % get_current_time())
        await self._start_gps_collector_thread()

    async def _start_gps_collector_thread(self):
        L.warning("\n[%s] Starting thread-level GPS Collector Worker" % get_current_time())
        t0_thread = time.time()
        pool_name = "[THREAD-%s]" % get_random_str()
        try:
            kwargs = {
                "pool_name": pool_name
            }
            self._executor.submit(self._spawn_gps_collector_worker, **kwargs)
        except:
            L.warning("\n[%s] Somehow we unable to Start the Thread of NodeGenerator" % get_current_time())
        t1_thread = (time.time() - t0_thread) * 1000
        L.warning('\n[%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_thread))
        # TODO: Save the latency into ElasticSearchDB for the real-time monitoring

    def _spawn_gps_collector_worker(self, pool_name):
        gps_data = [11.22, 44.22]
        while True:
            self._set_gps_data(gps_data)
            L.warning("\n[%s]%s Saving data in every 1 second; GPS data=%s" % (get_current_time(), pool_name, str(gps_data)))
            time.sleep(1)

    def _set_gps_data(self, gps_data):
        _gps_key = self._gps_key_prefix + self._drone_id
        redis_set(self._rc, _gps_key, gps_data)
