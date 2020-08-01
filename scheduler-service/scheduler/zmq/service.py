import asab
import logging
import imagezmq
import time
from scheduler.controllers.node.node import Node

###

L = logging.getLogger(__name__)


###


class ZMQService(asab.Service):
    """ A class to receive and send image data (numpy) through ZeroMQ protocol """

    def __init__(self, app, service_name="scheduler.ZMQService"):
        super().__init__(app, service_name)
        self.zmq_sender = []
        self.node_info = []

    # TODO: We need to have a dynamic configuration; This is still static and called ONCE
    async def set_configurations(self):
        print(" >>>>> @ ZMQ Sender: set_configurations")
        # Build ZMQ Senders
        node = Node()
        is_success, self.node_info, msg, total = node.get_data()

        print(" >>>> self.node_info:", self.node_info, type(self.node_info))
        if is_success:
            # Set ZMQ Senders
            for i in range(total):
                uri = 'tcp://127.0.0.1:555' + str(self.node_info[i]["name"])
                print(" >>>> uri:", uri)
                sender = imagezmq.ImageSender(connect_to=uri, REQ_REP=False)
                self.zmq_sender.append(sender)
        else:
            print(" >>>> Force to exit, since No Node are available!")
            exit()

    def get_senders(self):
        return {
            "zmq": self.zmq_sender,
            "node": self.node_info
        }

    def send_this_image(self, sender, frame_id, frame):
        t0_zmq = time.time()
        print("> >>>>>> START SENDING ZMQ in ts:", t0_zmq)
        zmq_id = str(frame_id) + "-" + str(t0_zmq)
        sender.send_image(zmq_id, frame)
        t1_zmq = (time.time() - t0_zmq) * 1000
        print('Latency [Send imagezmq] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
        # TODO: Saving latency for scheduler:latency:sending_image_zmq



