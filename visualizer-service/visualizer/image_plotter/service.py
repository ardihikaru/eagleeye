import asab
import logging
import time
from ext_lib.commons.util import plot_one_box
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_get, redis_set

###

L = logging.getLogger(__name__)


###


class ImagePlotterService(asab.Service):
    """
        A class to plot BBoxes into received images
    """

    def __init__(self, app, service_name="visualizer.ZMQService"):
        super().__init__(app, service_name)
        self.ImagePublisherService = app.get_service("visualizer.ImagePublisherService")
        self.redis = MyRedis(asab.Config)

    async def plot_img(self, is_latest_plot_available, frame_id, img):
        is_raw = bool(int(asab.Config["stream:config"]["is_raw"]))
        is_forced_plot = bool(int(asab.Config["stream:config"]["is_forced_plot"]))

        if not is_raw:
            # Collect latest `gps_data`;
            # // TODO HERE

            # Collect `plot_info`; wait until value `is not None; skip when `delay` > `wait_time`
            plot_info = await self._get_plot_info(str(frame_id))
            # print(plot_info)

            # If `plot_info` is not empty, save into redisDB (indicating the latest collected `plot_info`
            if bool(plot_info):
                if is_forced_plot:
                    await self._save_latest_plot_info(str(frame_id), plot_info)

                is_latest_plot_available = True

                # plot each mbbox data into the image
                for mbbox_data in plot_info["mbbox"]:
                    plot_one_box(mbbox_data, img, label=plot_info["label"], color=plot_info["color"])
                    break # TODO: This is a temporary approach! We need to fix the bug of PCS (v2)

            # This feature enable to plot PiH BBox based on the latest stored BBox in the redisDB
            # Default: ENABLED
            if is_forced_plot and not bool(plot_info) and is_latest_plot_available:
                plot_info = self._get_latest_plot_info(str(frame_id))
                if bool(plot_info):
                    # plot each mbbox data into the image
                    for mbbox_data in plot_info["mbbox"]:
                        plot_one_box(mbbox_data, img, label=plot_info["label"], color=plot_info["color"])
                        break  # TODO: This is a temporary approach! We need to fix the bug of PCS (v2)

        # write to pipe of RTSP Server
        await self.ImagePublisherService.publish_to_rstp_server(img)

        return is_latest_plot_available

    async def _get_plot_info(self, frame_id):
        drone_id = "1"  # TODO: hardcoded for NOW! need to be assigned dynamically later on!
        plot_info_key = "plotinfo-drone-%s-frame-%s" % (drone_id, frame_id)
        # plot_info = None
        # plot_info = redis_get(self.redis.get_rc(), plot_info_key)
        # print(plot_info)

        # wait until `plot_info` is not None
        max_delay = int(asab.Config["stream:config"]["delay"])
        t0_wait = time.time()
        t1_wait = 0.0
        while redis_get(self.redis.get_rc(), plot_info_key) is None:
            t1_wait = (time.time() - t0_wait) * 1000
            if t1_wait > max_delay:
                break
            continue

        L.warning("[FRAME Waiting time] of frame-%s=%s" % (frame_id, str(t1_wait)))
        plot_info = redis_get(self.redis.get_rc(), plot_info_key)

        return plot_info

    async def _save_latest_plot_info(self, frame_id, plot_info):
        drone_id = "1"  # TODO: hardcoded for NOW! need to be assigned dynamically later on!
        latest_plotinfo_key = "latest-plotinfo-drone-%s" % drone_id
        redis_set(self.redis.get_rc(), latest_plotinfo_key, plot_info)

    def _get_latest_plot_info(self, frame_id):
        drone_id = "1"  # TODO: hardcoded for NOW! need to be assigned dynamically later on!
        latest_plotinfo_key = "latest-plotinfo-drone-%s" % drone_id
        return redis_get(self.redis.get_rc(), latest_plotinfo_key)
