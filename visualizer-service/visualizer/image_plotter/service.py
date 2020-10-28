import asab
import logging
import time
from ext_lib.commons.util import plot_one_box
from ext_lib.redis.my_redis import MyRedis
from ext_lib.redis.translator import redis_get, redis_set
import cv2
from ext_lib.utils import get_current_time
from ext_lib.utils import get_imagezmq

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
        self.GPSCollectorService = app.get_service("visualizer.GPSCollectorService")
        self.redis = MyRedis(asab.Config)

        self._img_height = int(asab.Config["stream:config"]["height"])
        self._img_width = int(asab.Config["stream:config"]["width"])
        self._mode = asab.Config["stream:config"]["mode"]

    async def plot_img(self, is_latest_plot_available, frame_id, img):
        is_raw = bool(int(asab.Config["stream:config"]["is_raw"]))
        is_forced_plot = bool(int(asab.Config["stream:config"]["is_forced_plot"]))

        # collect latest GPS Data
        gps_data = await self.GPSCollectorService.get_gps_data()

        if not is_raw:
            # Collect `plot_info`; wait until value `is not None; skip when `delay` > `wait_time`
            plot_info = await self._get_plot_info(str(frame_id))

            # If `plot_info` is not empty, save into redisDB (indicating the latest collected `plot_info`
            pih_label = "PiH not Found"
            if bool(plot_info):
                pih_label = "PiH Found"
                if is_forced_plot:
                    await self._save_latest_plot_info(str(frame_id), plot_info)

                is_latest_plot_available = True

                # plot each mbbox data into the image
                t0_plot_bbox = time.time()
                for mbbox_data in plot_info["mbbox"]:
                    plot_one_box(mbbox_data, img, label=plot_info["label"], color=plot_info["color"])
                    break  # TODO: This is a temporary approach! We need to fix the bug of PCS (v2)
                t1_plot_bbox = (time.time() - t0_plot_bbox) * 1000
                L.warning('\n[%s] Latency for plotting PiH BBox (%.3f ms)' % (get_current_time(), t1_plot_bbox))

            self._plot_gps_and_det_info(gps_data, pih_label, img)
            self._plot_fps_info(img, 30)  # TODO: This constant FPS should be calculated from the fetched images!

            # This feature enable to plot PiH BBox based on the latest stored BBox in the redisDB
            # Default: DISABLED
            if is_forced_plot and not bool(plot_info) and is_latest_plot_available:
                plot_info = self._get_latest_plot_info(str(frame_id))
                if bool(plot_info):
                    # plot each mbbox data into the image
                    for mbbox_data in plot_info["mbbox"]:
                        plot_one_box(mbbox_data, img, label=plot_info["label"], color=plot_info["color"])
                        break  # TODO: This is a temporary approach! We need to fix the bug of PCS (v2)

        if self._mode == "rtsp":
            # write to pipe of RTSP Server
            await self.ImagePublisherService.publish_to_rstp_server(img)

        return is_latest_plot_available

    def _plot_gps_and_det_info(self, gps_data, det_status, img):
        t0_plot_gps_det = time.time()
        x_coord_lbl, y_coord_lbl = 10, (self._img_height - 90)
        x_coord_gps, y_coord_gps = 10, (self._img_height - 60)
        x_coord_obj, y_coord_obj = 10, (self._img_height - 30)
        gps_ts = time.strftime('%H:%M:%S', time.localtime(gps_data["timestamp"]))
        long = gps_data["gps"]["long"]
        lat = gps_data["gps"]["lat"]
        alt = gps_data["gps"]["alt"]

        # Set labels
        gps_title_label = "GPS Information (%s):" % gps_ts
        gps_data_label = "LONG= %f; LAT= %f; ALT= %f;" % (long, lat, alt)
        obj_data_label = "Detection status: %s" % det_status

        # Add filled box
        # tl = round(0.002 * (self.img.shape[0] + self.img.shape[1]) / 2) + 1  # line thickness
        tl = round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line thickness
        tf = max(tl - 1, 1)  # font thickness
        t_size_title = cv2.getTextSize(gps_data_label, 0, fontScale=tl / 3, thickness=tf)[0]
        t_size = cv2.getTextSize(gps_data_label, 0, fontScale=tl / 3, thickness=tf)[0]
        t_size_obj = cv2.getTextSize(gps_data_label, 0, fontScale=tl / 3, thickness=tf)[0]
        c1 = (int(x_coord_lbl), int(y_coord_lbl - 30))
        c2 = x_coord_obj + t_size_title[0] - 300, y_coord_obj - t_size_obj[1] + 40

        cv2.rectangle(img, c1, c2, [0, 0, 0], -1)  # filled

        cv2.putText(img, gps_title_label,
                    (x_coord_lbl, y_coord_lbl), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        cv2.putText(img, gps_data_label,
                    (x_coord_gps, y_coord_gps), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        # Plot detection status
        cv2.putText(img, obj_data_label,
                    (x_coord_obj, y_coord_obj), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        t1_plot_gps_det = (time.time() - t0_plot_gps_det) * 1000
        L.warning('\n[%s] Latency for plotting GPS and detection information (%.3f ms)' % (get_current_time(),
                                                                                           t1_plot_gps_det))

    def _plot_fps_info(self, img, fps=None):
        t0_plot_fps = time.time()
        x_coord, y_coord = (self._img_width - 300), 40

        # Set labels
        if fps is None:
            label = "FPS: None"
        else:
            label = "FPS: %.2f" % fps

        # Add filled box: FPS
        tl = round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line thickness
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c1 = (int(x_coord), int(y_coord))
        c2 = x_coord + t_size[0] + 30, y_coord - t_size[1] - 3
        cv2.rectangle(img, c1, c2, [0, 0, 0], -1)  # filled
        cv2.putText(img, label, (x_coord, y_coord), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)

        t1_plot_fps = (time.time() - t0_plot_fps) * 1000
        L.warning('\n[%s] Latency for plotting FPS information (%.3f ms)' % (get_current_time(),
                                                                                           t1_plot_fps))

    async def _get_plot_info(self, frame_id):
        drone_id = "1"  # TODO: hardcoded for NOW! need to be assigned dynamically later on!
        plot_info_key = "plotinfo-drone-%s-frame-%s" % (drone_id, frame_id)

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
