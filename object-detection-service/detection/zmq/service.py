import asab
import logging
import time
import imagezmq
from ext_lib.zeromq.zmqimage import ZMQImageServer

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
        print(" ### @ set_configurations ...")
        uri = asab.Config["zmq"]["node_uri"]
        print(" >>>>>>>>>> URI ZMQ=", uri)
        # channel = asab.Config["zmq"]["node_channel"]
        # self.zmq_receiver = imagezmq.ImageHub(open_port=uri, REQ_REP=False)
        self.zmq_receiver = ZMQImageServer(open_port=uri)
        print(" >>>> self.zmq_receiver:", self.zmq_receiver)
    #     # Collect available nodes
    #     node = Node()
    #     is_success, self.node_info, msg, total = node.get_data()
    #
    #     print(" >>>> self.node_info:", self.node_info, type(self.node_info))
    #     if is_success:
    #         # Set ZMQ Senders
    #         for i in range(total):
    #             url = 'tcp://127.0.0.1:555' + str((i + 1))
    #             sender = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
    #             self.zmq_sender.append(sender)
    #

    def get_zmq_receiver(self):
        return self.zmq_receiver
