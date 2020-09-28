import asab
import logging
import imagezmq
from ext_lib.redis.my_redis import MyRedis

###

L = logging.getLogger(__name__)


###


class ZMQService(asab.Service):
    """
        A class to receive and send image data (numpy) through ZeroMQ protocol
    """

    def __init__(self, app, service_name="detection.ZMQService"):
        super().__init__(app, service_name)
        self.zmq_receiver = None

    # TODO: We need to have a dynamic configuration; This is still static and called ONCE
    async def set_configurations(self, node_name, node_id):  # node_name is the port suffix!
        # get node name
        uri = "tcp://%s:%s%s" % (asab.Config["zmq"]["sender_host"], asab.Config["zmq"]["sender_prefix_port"], node_name)
        L.warning("[IMPORTANT] Accepted ZMQ URI: %s" % uri)
        self.zmq_receiver = imagezmq.ImageHub(open_port=uri, REQ_REP=False)

    def get_zmq_receiver(self):
        return self.zmq_receiver
