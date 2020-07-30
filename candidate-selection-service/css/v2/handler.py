import asab
import logging
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import get_current_time
import os

###

L = logging.getLogger(__name__)


###

class CSSv2Handler(MyRedis):

    def __init__(self, app):
        super().__init__(asab.Config)
        # self.CSSv2Service = app.get_service("css.CSSv2Service")
        self.storage = app.get_service("asab.StorageService")

    async def set_configuration(self):
        # Initialize CSSv2 configuration
        print("\n[%s] Initialize CSSv2 configuration" % get_current_time())

        coll = await self.storage.collection("Users")
        cursor = coll.find({})
        print("Result of list *** DISINI ***")
        while await cursor.fetch_next:
            obj = cursor.next_object()
            print(obj)

    async def stop(self):
        print("\n[%s] Candidate Selection Service is going to stop" % get_current_time())
        exit()

    async def start(self):
        print("\n[%s] CSSv2Handler try to consume the published data from [Object Detection Service]" % get_current_time())

        pid = os.getpid()
        print(" --- Candidate Selection Service's PID", pid)

        # Sample actions
        import time
        import signal
        for i in range(100):
            my_pid = os.getpid()
            print("## %s ## I am running, dude. >>> PID=" % i, my_pid)
            time.sleep(1)

            if i == 10:
                print(" >>> I AM KILLING MYSELF!!! pid=", pid)
                await self.stop()
