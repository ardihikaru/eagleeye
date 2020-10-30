import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_set, redis_get
from ext_lib.utils import get_current_time, get_random_str
from concurrent.futures import ThreadPoolExecutor
import time
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

    def __init__(self, app, service_name="ews.GPSCollectorService"):
        super().__init__(app, service_name)
        _redis = MyRedis(asab.Config)
        self._rc = _redis.get_rc()
        # self._drone_id = asab.Config["stream:config"]["drone_id"]  # TODO: DroneID should be DYNAMIC!
        self._gps_key_prefix = asab.Config["stream:config"]["gps_key_prefix"]
        self._executor = ThreadPoolExecutor(int(asab.Config["thread"]["num_executor"]))
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
        self._drone_gps_data = self._build_dummy_gps_data()

        self._start_gps_collector_thread()

    async def initialize(self, app):
        L.warning("\n[%s] Initializing GPS Collector Service" % get_current_time())

    def _initialize_connection_mode(self):
        if self._collector_mode == "online":
            # Validate connection with the target URL
            if self._is_ip_reachable():
                self._is_online = True
                self._setup_soap_connection()
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
        self._client = Client(self._target_url)
        print(" #### self._client ...")
        print(self._client)

    def _build_conn_url(self):
        schema = asab.Config["stream:gps"]["schema"]
        host = asab.Config["stream:gps"]["host"]
        port = asab.Config["stream:gps"]["port"]
        path = asab.Config["stream:gps"]["path"]
        self._target_url = "{}://{}:{}/{}".format(schema, host, port, path)

    def _build_dummy_gps_data(self):
        dummy_gps_data = []
        gps_data = self._default_drone_gps_data
        for i in range(self._num_drones):
            gps_data["FlyNo"] = str(int(gps_data["FlyNo"]) + 1)
            gps_data["Latitude"] = str(float(gps_data["Latitude"]) + 1)
            gps_data["Longitude"] = str(float(gps_data["Longitude"]) + 1)
            gps_data["Altitude"] = str(int(gps_data["Altitude"]) + 1)
            dummy_gps_data.append(gps_data.copy())

        return dummy_gps_data

    def _start_gps_collector_thread(self):
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
        dummy_gps_data = self._drone_gps_data

        while True:
            # all_gps_data = self._extract_and_build_gps_data(dummy_gps_data)
            all_gps_data = self._get_latest_drone_gps_data(dummy_gps_data)

            for each_gps_data in all_gps_data:
                self._set_gps_data(each_gps_data["drone_id"], each_gps_data)
                L.warning("[{}]{} Saving data in every 1 second; GPS data (drone_id=`{}`)={}".format(
                    get_current_time(), pool_name, each_gps_data["drone_id"], str(each_gps_data["gps"]))
                )
            L.warning("")
            time.sleep(1)

            # OFFLINE MODE: Simulate drone movement (Lat, Long, Alt)
            if not self._is_online:
                dummy_gps_data = self._simulate_drone_movement(dummy_gps_data)

    def _get_latest_drone_gps_data(self, dummy_gps_data):
        if not self._is_online:
            return self._extract_and_build_gps_data(dummy_gps_data)
        else:
            return self._extract_gps_data()

    def _extract_gps_data(self):
        try:
            raw_gps_data = self._client.service.GetAllDroneState()
            raw_gps_data = ''.join(raw_gps_data)
            print(" #### raw_gps_data ...")
            print(raw_gps_data)
            print()
            return json.loads(raw_gps_data)
        except Exception as e:
            L.error("Unable to capture and extract GPS Data: {}".format(e))
            return None

    def _simulate_drone_movement(self, drone_gps_data):
        for i in range(len(drone_gps_data)):
            # Update only Lat, Long, and Alt
            drone_gps_data[i]["Latitude"] = str(float(drone_gps_data[i]["Latitude"]) + 1)
            drone_gps_data[i]["Longitude"] = str(float(drone_gps_data[i]["Longitude"]) + 1)
            drone_gps_data[i]["Altitude"] = str(float(drone_gps_data[i]["Altitude"]) + 1)
        return drone_gps_data.copy()

    def _extract_and_build_gps_data(self, drone_gps_data):
        extracted_gps_data = []
        for each_gps_data in drone_gps_data:
            gps_data = {
                "drone_id": each_gps_data["FlyNo"],
                "timestamp": time.time(),
                "drone_timestamp": each_gps_data["Timestamp"],
                "heading": float(each_gps_data["Heading"]),
                "groundSpeed": float(each_gps_data["GroundSpeed"]),
                "gps": {
                    "long": float(each_gps_data["Longitude"]),
                    "lat": float(each_gps_data["Latitude"]),
                    "alt": float(each_gps_data["Altitude"])
                },
                "xyz": {
                    "pitch": float(each_gps_data["Pitch"]),
                    "roll": float(each_gps_data["Roll"]),
                    "yaw": float(each_gps_data["Yaw"])
                }
            }
            extracted_gps_data.append(gps_data.copy())

        return extracted_gps_data

    def _collect_gps_data(self):
        if self._is_online:
            pass
        else:
            pass

    def _set_gps_data(self, drone_id, gps_data):
        # _gps_key = self._gps_key_prefix + self._drone_id
        _gps_key = self._gps_key_prefix + drone_id
        redis_set(self._rc, _gps_key, gps_data)
