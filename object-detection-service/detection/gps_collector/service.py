import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_set, redis_get
import simplejson as json

###

L = logging.getLogger(__name__)


###


class GPSCollectorService(asab.Service):
    """
        GPS Collector Service
    """

    def __init__(self, app, service_name="detection.gpsCollectorService"):
        super().__init__(app, service_name)
        _redis = MyRedis(asab.Config)
        self._rc = _redis.get_rc()
        self._drone_id = asab.Config["stream:config"]["drone_id"]  # TODO: DroneID should be DYNAMIC!
        self._gps_key_prefix = asab.Config["stream:config"]["gps_key_prefix"]

    async def get_gps_data(self, drone_id):
        gps_data = None
        while gps_data is None:
            _gps_key = self._gps_key_prefix + drone_id
            gps_data = redis_get(self._rc, _gps_key)
            if gps_data is None:
                continue
            else:
                gps_data = json.loads(gps_data)
        return gps_data
