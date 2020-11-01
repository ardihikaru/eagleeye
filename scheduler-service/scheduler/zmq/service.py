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
        self.zmq_visualizer = None
        self.zmq_source_reader = None
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

        zmq_host = asab.Config["zmq"]["sender_host"]
        if is_success:
            # Set ZMQ Sender for sending image to Worker Nodes
            # Builds ZMQ Senders
            for i in range(total):
                # uri = 'tcp://%s:555' % zmq_host + str(self.node_info[i]["name"])
                uri = self._set_zmq_uri(zmq_host, i)
                L.warning("ZMQ URI: %s" % uri)
                sender = imagezmq.ImageSender(connect_to=uri, REQ_REP=False)
                self.zmq_sender.append(sender)

            # Set ZMQ Sender for sending images to Visualizer Service
            # build ZMQ URI
            visualizer_port = asab.Config["zmq"]["visualizer_port"]
            visualizer_uri = 'tcp://%s:%s' % (zmq_host, visualizer_port)
            L.warning("ZMQ Visualizer URI: %s" % visualizer_uri)
            self.zmq_visualizer = imagezmq.ImageSender(connect_to=visualizer_uri, REQ_REP=False)

        else:
            # print("\n[%s] Forced to exit, since No Node are available!" % get_current_time())
            L.warning("\n[%s] Forced to exit, since No Node are available!" % get_current_time())
            exit()

    async def initialize_zmq_source_reader(self, zmq_source_host, zmq_source_port):
        img_source_uri = 'tcp://%s:%s' % (zmq_source_host, zmq_source_port)
        L.warning("ZMQ Source Reader URI: %s" % img_source_uri)
        self.zmq_source_reader = imagezmq.ImageHub(open_port=img_source_uri, REQ_REP=False)

    def get_zmq_source_reader(self):
        return self.zmq_source_reader

    def get_imagezmq(self, zmq_receiver):
        try:
            array_name, image = zmq_receiver.recv_image()
            tmp = array_name.split("-")
            frame_id = int(tmp[0])
            t0 = float(tmp[1])
            return True, frame_id, t0, image

        except Exception as e:
            L.error("[ERROR]: %s" % str(e))
            return False, None, None, None

    def _set_zmq_uri(self, zmq_host, i):
        if asab.Config["orchestration"]["mode"] == "native":
            return 'tcp://%s:555' % zmq_host + str(self.node_info[i]["name"])
        else:
            # Multiple ports, broadcast network (*)
            return 'tcp://%s:555%s' % (
                asab.Config["zmq"]["sender_host"],
                str(self.node_info[i]["name"])
            )
            # # Single port, multiple hosts (ERROR)
            # return 'tcp://%s-%s:5551' % (
            #     asab.Config["zmq"]["recv_host_prefix"],
            #     str(self.node_info[i]["name"])
            # )

    def get_senders(self):
        return {
            "zmq": self.zmq_sender,
            "node": self.node_info
        }

    def get_available_nodes(self):
        return self.node_info

    def send_this_image(self, sender, frame_id, frame):
        t0_zmq = time.time()
        zmq_id = str(frame_id) + "-" + str(t0_zmq)
        sender.send_image(zmq_id, frame)
        t1_zmq = (time.time() - t0_zmq) * 1000
        L.warning('Latency [Send imagezmq] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
        # TODO: Saving latency for scheduler:latency:sending_image_zmq

    def send_image_to_visualizer(self, frame_id, frame):
        t0_zmq = time.time()
        zmq_id = str(frame_id) + "-" + str(t0_zmq)
        self.zmq_visualizer.send_image(zmq_id, frame)
        t1_zmq = (time.time() - t0_zmq) * 1000
        L.warning('Latency [Send image to Visualizer] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))
        # TODO: Saving latency for scheduler:latency:sending_image_zmq

