import asab
import logging
import imagezmq
import time
from ext_lib.utils import get_current_time
import requests 

###

L = logging.getLogger(__name__)


###


class ZMQService(asab.Service):
    """ A class to receive and send image data (numpy) through ZeroMQ protocol """

    def __init__(self, app, service_name="scheduler.ZMQService"):
        super().__init__(app, service_name)
        self.zmq_sender = []
        self.node_info = []
        self.node_api_uri = asab.Config["eagleeye:api"]["node"]

    # TODO: We need to have a dynamic configuration; This is still static and called ONCE
    async def set_configurations(self):
        # sending get request and saving the response as response object
        req = requests.get(url=self.node_api_uri)

        # extracting data in json format
        data = req.json()

        is_success = data["success"]
        self.node_info = data["data"]
        total = int(data["total"])

        zmq_uri = asab.Config["zmq"]["sender_uri"]
        L.info("ZMQ URI: %s" % zmq_uri)

        if is_success:
            # Builds ZMQ Senders
            for i in range(total):
                # uri = 'tcp://127.0.0.1:555' + str(self.node_info[i]["name"])
                uri = 'tcp://%s:555' % zmq_uri + str(self.node_info[i]["name"])
                sender = imagezmq.ImageSender(connect_to=uri, REQ_REP=False)
                self.zmq_sender.append(sender)
        else:
            print("\n[%s] Forced to exit, since No Node are available!" % get_current_time())
            exit()

    def get_senders(self):
        return {
            "zmq": self.zmq_sender,
            "node": self.node_info
        }

    def get_available_nodes(self):
        return self.node_info

    def send_this_image(self, sender, frame_id, frame):
        t0_zmq = time.time()
        # print("> >>>>>> START SENDING ZMQ in ts:", t0_zmq)
        zmq_id = str(frame_id) + "-" + str(t0_zmq)
        sender.send_image(zmq_id, frame)
        t1_zmq = (time.time() - t0_zmq) * 1000
        print('Latency [Send imagezmq] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
        # TODO: Saving latency for scheduler:latency:sending_image_zmq



