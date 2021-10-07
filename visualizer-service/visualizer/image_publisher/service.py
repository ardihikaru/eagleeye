import asab
import logging
import subprocess
from ext_lib.redis.my_redis import MyRedis
from asab import LOG_NOTICE

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
        ffmpeg_gpu = asab.Config["stream:config"].getboolean("gpu_enabled")  # default true

        # build rtsp URI
        protocol = asab.Config["stream:config"]["protocol"]
        host = asab.Config["stream:config"]["host"]
        path = asab.Config["stream:config"]["path"]
        rtsp_url = "%s://%s/%s" % (protocol, host, path)
        L.log(LOG_NOTICE, "Setup RTSP URL: {}".format(rtsp_url))

        mode = asab.Config["stream:config"]["mode"]

        # command and params for ffmpeg
        if ffmpeg_gpu:
            _command = ['ffmpeg',
                        '-y',
                        '-f', 'rawvideo',
                        '-vcodec', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', "{}x{}".format(width, height),
                        '-r', fps,
                        '-i', '-',
                        '-pix_fmt', 'yuv420p',
                        '-preset', 'ultrafast',
                        '-f', 'rtsp',
                        rtsp_url]
        else:
            _command = ['ffmpeg',
                        '-y',
                        '-f', 'rawvideo',
                        '-vcodec', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', "{}x{}".format(width, height),
                        '-r', fps,
                        '-i', '-',
                        '-c:v', 'libx264',  # this is removed on the GPU-enabled ffmpeg
                        '-pix_fmt', 'yuv420p',
                        '-preset', 'ultrafast',
                        '-f', 'rtsp',
                        rtsp_url]

        # if `mode` != `rtsp`, no need to create a subprocess
        if mode == "rtsp":
            # using subprocess and pipe to fetch frame data
            self._sp = subprocess.Popen(_command, stdin=subprocess.PIPE)

    async def publish_to_rstp_server(self, img):
        self._sp.stdin.write(img.tobytes())
