import asab
import logging
import time
import imagezmq
from scheduler.controllers.node.node import Node
from ext_lib.zeromq.zmqimage import ZMQConnect

###

L = logging.getLogger(__name__)


###


class ZMQService(asab.Service):
    """
        A class to receive and send image data (numpy) through ZeroMQ protocol
    """

    def __init__(self, app, service_name="scheduler.ZMQService"):
        super().__init__(app, service_name)
        self.zmq_sender = []
        self.node_info = []

    # TODO: We need to have a dynamic configuration; This is still static and called ONCE
    async def set_configurations(self):
        # Collect available nodes
        node = Node()
        is_success, self.node_info, msg, total = node.get_data()

        print(" >>>> self.node_info:", self.node_info, type(self.node_info))
        if is_success:
            # Set ZMQ Senders
            for i in range(total):
                # url = 'tcp://127.0.0.1:555' + str((i + 1))
                uri = 'tcp://127.0.0.1:556' + str(self.node_info[i]["name"])
                print(" >>>> uri:", uri)
                # sender = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
                sender = ZMQConnect(connect_to=uri)
                self.zmq_sender.append(sender)
        else:
            print(" >>>> Force to exit, since No Node are available!")
            exit()

    def get_senders(self):
        return {
            "zmq": self.zmq_sender,
            "node": self.node_info
        }
