import asab
import logging
import imagezmq
import subprocess

###

L = logging.getLogger(__name__)


###


class ZMQService(asab.Service):
    """
        A class to receive and send image data (numpy) through ZeroMQ protocol
    """

    def __init__(self, app, service_name="visualizer.ZMQService"):
        super().__init__(app, service_name)
        self.zmq_receiver = None

        # gather video info to ffmpeg
        fps = asab.Config["streaming"]["fps"]
        width = int(asab.Config["streaming"]["width"])
        height = int(asab.Config["streaming"]["height"])

        # build rtsp URI
        protocol = asab.Config["streaming"]["protocol"]
        host = asab.Config["streaming"]["host"]
        path = asab.Config["streaming"]["path"]
        rtsp_url = "%s://%s/%s" % (protocol, host, path)

        # command and params for ffmpeg
        _command = ['ffmpeg',
                         '-y',
                         '-f', 'rawvideo',
                         '-vcodec', 'rawvideo',
                         '-pix_fmt', 'bgr24',
                         '-s', "{}x{}".format(width, height),
                         '-r', fps,
                         '-i', '-',
                         '-c:v', 'libx264',
                         '-pix_fmt', 'yuv420p',
                         '-preset', 'ultrafast',
                         '-f', 'rtsp',
                         rtsp_url]

        # using subprocess and pipe to fetch frame data
        self._sp = subprocess.Popen(_command, stdin=subprocess.PIPE)

    async def set_configurations(self):
        uri = "tcp://%s:%s" % (asab.Config["zmq"]["sender_host"], asab.Config["zmq"]["sender_port"])
        L.warning("[IMPORTANT] Accepted ZMQ URI: %s" % uri)
        self.zmq_receiver = imagezmq.ImageHub(open_port=uri, REQ_REP=False)

    def get_zmq_receiver(self):
        return self.zmq_receiver

    async def _set_zmq_configurations(self):
        await self.set_configurations()

    def _get_imagezmq(self):
        try:
            array_name, image = self.get_zmq_receiver().recv_image()
            tmp = array_name.split("-")
            frame_id = int(tmp[0])
            t0 = float(tmp[1])
            return True, frame_id, t0, image

        except Exception as e:
            L.error("[ERROR]: %s" % str(e))
            return False, None, None, None

    async def start(self):
        await self._set_zmq_configurations()
        L.warning("I am running ...")
        while True:
            is_success, frame_id, t0_zmq, img = self._get_imagezmq()
            if is_success:
                # write to pipe of RTSP Server
                self._sp.stdin.write(img.tobytes())
