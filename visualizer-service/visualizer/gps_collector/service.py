import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_set, redis_get
import time
from ext_lib.utils import get_current_time
from suds.client import Client
import simplejson as json
import subprocess
from subprocess import Popen, PIPE

###

L = logging.getLogger(__name__)


###


class GPSCollectorService(asab.Service):
    """
        GPS Collector Service
    """

    def __init__(self, app, service_name="visualizer.GPSCollectorService"):
        super().__init__(app, service_name)
        _redis = MyRedis(asab.Config)
        self._rc = _redis.get_rc()
        self._drone_id = asab.Config["stream:config"]["drone_id"]  # TODO: DroneID should be DYNAMIC!
        self._gps_key_prefix = asab.Config["stream:config"]["gps_key_prefix"]

        self._collector_mode = asab.Config["stream:gps"]["mode"]
        self._num_drones = int(asab.Config["stream:gps"]["num_drones"])
        self._drone_gps_data = []
        self._target_url = None
        self._client = None
        self._is_online = False
        self._default_drone_gps_data = {
            "FlyNo": "0",
            "Latitude": "25.0334931",
            "Longitude": "121.5641012",
            "Altitude": "10",
            "Heading": "360",
            "GroundSpeed": "10",
            "Pitch": "-0.00841480027884245",
            "Roll": "-0.0021843130234628916",
            "Yaw": "2.517401695251465",
            "Timestamp": 1603977660
          }

        self._build_conn_url()
        self._initialize_connection_mode()

    async def initialize(self, app):
        L.warning("\n[%s] Initializing GPS Collector Service" % get_current_time())

    def _initialize_connection_mode(self):
        if self._collector_mode == "online":
            # Validate connection with the target URL
            if self._is_ip_reachable():
                self._is_online = True
                self._setup_soap_connection()
                if self._client is None:
                    L.warning("[WARNING!] ******* GPS COLLECTOR IS WORKING IN AN OFFLINE MODE !!!!")
                else:
                    L.warning("[IMPORTANT!] ******* GPS COLLECTOR IS WORKING IN AN ONLINE MODE !!!!")
            else:
                L.warning("[WARNING!] ******* GPS COLLECTOR IS WORKING IN AN OFFLINE MODE !!!!")
        else:
            L.warning("[WARNING!] ******* GPS COLLECTOR IS WORKING IN AN OFFLINE MODE !!!!")

    def _is_ip_reachable(self):
        hostname = asab.Config["stream:gps"]["host"]
        process = subprocess.Popen(['ping', '-c', '5', '-w', '5', hostname],
                                   stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        packetloss = float(
            [x for x in stdout.decode('utf-8').split('\n') if x.find('packet loss') != -1][0].split('%')[0].split(' ')[
                -1])
        if packetloss > 10.0:  # TODO: constant value can be used dynamically in the future
            L.error("[WARNING!] Unable to connect with {}".format(hostname))
            return False
        else:
            return True

    def _setup_soap_connection(self):
        try:
            self._client = Client(self._target_url)
        except Exception as e:
            L.warning("Connection establishment Failed; Reason: {}".format(e))

    def _build_conn_url(self):
        schema = asab.Config["stream:gps"]["schema"]
        host = asab.Config["stream:gps"]["host"]
        port = asab.Config["stream:gps"]["port"]
        path = asab.Config["stream:gps"]["path"]
        self._target_url = "{}://{}:{}/{}".format(schema, host, port, path)

    async def get_gps_data(self, drone_id=None):
        t0_gps = time.time()
        if drone_id is None:
            drone_id = self._drone_id

        _gps_key = self._gps_key_prefix + drone_id
        gps_data = None
        while gps_data is None:
            gps_data = redis_get(self._rc, _gps_key)
            if gps_data is None:
                continue

        t1_gps = (time.time() - t0_gps) * 1000
        L.warning('\n[%s] Latency for collecting GPS data (%.3f ms)' % (get_current_time(), t1_gps))
        return gps_data

    async def _sending_fake_request(self, gps_data):
        L.warning(" **** I am in OFFLINE Mode. FlyNo={}; GPS={}".format(gps_data["fly_no"], gps_data["gps"]))

    async def _sending_real_request(self, gps_data):
        soap_request_obj = {
            "FlyNo": gps_data["fly_no"],
            "lat": str(gps_data["gps"]["lat"]),
            "lon": str(gps_data["gps"]["long"]),
            "Alt": str(gps_data["gps"]["alt"])
        }
        soap_request = json.dumps(soap_request_obj)
        t0_soap_askey = time.time()
        resp = self._client.service.SendPeopleLocation(soap_request)
        t1_soap_askey = (time.time() - t0_soap_askey) * 1000
        L.warning('\n[%s] Latency for ASKEY SOAP response (%.3f ms)' % (get_current_time(), t1_soap_askey))
        resp = ''.join(resp)
        resp = json.loads(resp)
        if "Response" in resp and resp["Response"] == "OK":
            L.warning(" **** GPS Information have been successfully sent into ASKEY's Drone Navigation Server.")
            L.warning("-- GPS INFO --> FlyNo={}; GPS={}".format(gps_data["fly_no"], gps_data["gps"]))
        else:
            L.warning("UNABLE TO SEND GPS Information (Reason: {}). FlyNo={}; GPS={}".format(resp, gps_data["fly_no"],
                                                                                             gps_data["gps"]))

    async def send_gps_info(self, gps_data):
        print(">>> gps_data:", gps_data)
        if self._is_online:
            await self._sending_real_request(gps_data)
        else:
            await self._sending_fake_request(gps_data)
