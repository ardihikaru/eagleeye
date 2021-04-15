import asab
import logging
from ext_lib.utils import get_current_time
import socket
import numpy
import cv2

###

L = logging.getLogger(__name__)


###


class TCPCameraServerService(asab.Service):
    """ A class to receive and send image data (numpy) through TCP protocol """

    def __init__(self, app, service_name="scheduler.TCPCameraServerService"):
        super().__init__(app, service_name)
        self.tcp_source_reader = None
        self.conn, self.addr = None, None

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    async def initialize_camera_source_reader(self, _tcp_host, _tcp_port):
        L.warning(" *** TCP Source Info; Host={}; Port={}".format(_tcp_host, _tcp_port))

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((_tcp_host, _tcp_port))
        s.listen(True)
        self.conn, self.addr = s.accept()

    def get_tcp_conn(self):
        return self.conn

    async def get_image(self, frame_id):
        _width = int(asab.Config["stream:config"]["width"])
        _height = int(asab.Config["stream:config"]["height"])

        length = self.recvall(self.conn, 16)
        length = length.decode('utf-8')
        stringData = self.recvall(self.conn, int(length))
        # stringData = zlib.decompress(stringData)
        # print('old={} new={}'.format(len(stringData), len(zlib.compress(stringData)) ))
        data = numpy.fromstring(stringData, dtype='uint8')
        decimg = cv2.imdecode(data, 1)

        # Validate input image resolution
        # If the resolution is not Full HD, then, force resizing it into FUll HD (1920 x 1080)
        source_shape = list(decimg.shape)  # [heigh, width]
        if source_shape[0] != _width and source_shape[1] != _height:
            decimg = cv2.resize(decimg, (_width, _height))

        L.warning(" *** Frame size:{}".format(decimg.shape))

        return True, frame_id, 0.0, decimg
