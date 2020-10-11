import asab
import logging
import imagezmq
import subprocess
import time
from ext_lib.commons.util import plot_one_box
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_get, redis_set

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

    async def _get_plot_info(self, frame_id):
        drone_id = "1"  # TODO: hardcoded for NOW! need to be assigned dynamically later on!
        plot_info_key = "plotinfo-drone-%s-frame-%s" % (drone_id, frame_id)
        # plot_info = None
        # plot_info = redis_get(self.redis.get_rc(), plot_info_key)
        # print(plot_info)

        # wait until `plot_info` is not None
        while redis_get(self.redis.get_rc(), plot_info_key) is None:
            continue

        plot_info = redis_get(self.redis.get_rc(), plot_info_key)
        print(plot_info)

        if bool(plot_info):
            # TODO: To be refactored and be implemented in a more elegant way!
            # Change color into list of int
            color = plot_info["color"].strip('][').split(', ')
            for i in range(len(color)):
                color[i] = int(color[i])

            plot_info["color"] = color

        print(" >>> PLOT BARU")
        print(plot_info)

        return plot_info

    async def _save_latest_plot_info(self, frame_id, plot_info):
        print(" >>> **** plot_info has MBBox data! Store into redisDB")
        drone_id = "1"  # TODO: hardcoded for NOW! need to be assigned dynamically later on!
        latest_plotinfo_key = "latest-plotinfo-drone-%s-frame-%s" % (drone_id, frame_id)
        redis_set(self.redis.get_rc(), latest_plotinfo_key, plot_info)

    async def start(self):
        await self._set_zmq_configurations()
        L.warning("I am running ...")
        while True:
            is_success, frame_id, t0_zmq, img = self._get_imagezmq()
            t1_zmq = (time.time() - t0_zmq) * 1000
            if is_success:
                L.warning('Latency [Visualizer Capture] of frame-%s: (%.5fms)' % (str(frame_id), t1_zmq))

                # Collect latest `gps_data`;
                # // TODO HERE

                # Collect `plot_info`; wait until value `is not None; skip when `delay` > `wait_time`
                plot_info = await self._get_plot_info(str(frame_id))

                # If `plot_info` is not empty, save into redisDB (indicating the latest collected `plot_info`
                if bool(plot_info):
                    await self._save_latest_plot_info(str(frame_id), plot_info)

                    # plot each mbbox data into the image
                    for mbbox_data in plot_info["mbbox"]:
                        plot_one_box(mbbox_data, img, label=plot_info["label"], color=plot_info["color"])

                # write to pipe of RTSP Server
                self._sp.stdin.write(img.tobytes())
