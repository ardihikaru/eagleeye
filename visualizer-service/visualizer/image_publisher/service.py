import asab
import logging
import subprocess
from ext_lib.redis.my_redis import MyRedis

###

L = logging.getLogger(__name__)


###


class ImagePublisherService(asab.Service):
    """
        A class to publish image/frame into RTSP Server through pipeline (subprocess)
    """

    def __init__(self, app, service_name="visualizer.ZMQService"):
        super().__init__(app, service_name)
        self.redis = MyRedis(asab.Config)

        # gather video info to ffmpeg
        fps = asab.Config["stream:config"]["fps"]
        width = int(asab.Config["stream:config"]["width"])
        height = int(asab.Config["stream:config"]["height"])

        # build rtsp URI
        protocol = asab.Config["stream:config"]["protocol"]
        host = asab.Config["stream:config"]["host"]
        path = asab.Config["stream:config"]["path"]
        rtsp_url = "%s://%s/%s" % (protocol, host, path)
        L.warning("Setup RTSP URL: %s" % rtsp_url)

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

    async def publish_to_rstp_server(self, img):
        self._sp.stdin.write(img.tobytes())
