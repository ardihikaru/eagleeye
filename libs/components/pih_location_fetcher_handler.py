from libs.settings import common_settings
from libs.algorithms.pih_location_fetcher import PIHLocationFetcher
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_get, pub, redis_set
import simplejson as json
import time
import imagezmq


class PIHLocationFetcherHandler(MyRedis):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        self.plf_send_status_channel = "plf-send-status"
        self.plf_bbox_receiver_channel_pre = "plf-receiver-bbox"
        self.drone_id = None
        self.frame_id = 0
        self.worker_id = None
        self.raw_image = None
        self.plotted_img = None
        self.visual_type = -1
        self.bbox = []
        self.mbbox = []
        self.__set_plf_receiver()

        self.visual_sender = []
        self.__set_visual_sender()

    # Visualizer
    def __set_visual_sender(self):
        for i in range(self.opt.total_drones):
            this_drone_id = i + 1
            port = self.opt.visualizer_port_prefix + str(this_drone_id)
            url = 'tcp://127.0.0.1:' + port
            this_visual_sender = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
            self.visual_sender.append(this_visual_sender)

    # PiH Location Fetcher (plf)
    def __set_plf_receiver(self):
        url = 'tcp://127.0.0.1:' + str(self.opt.pih_location_fetcher_port)
        self.frame_receiver = imagezmq.ImageHub(open_port=url, REQ_REP=False)

    def run(self):
        self.watch_frame_sender()

    def capture_extracted_frame_data(self, frame_data):
        self.drone_id = frame_data["drone_id"]
        self.frame_id = frame_data["frame_id"]
        self.visual_type = frame_data["visual_type"]

    # Sent by: `video_streamer.py`
    def watch_frame_sender(self):
        pub_sub_sender = self.rc_data.pubsub()
        pub_sub_sender.subscribe([self.plf_send_status_channel])
        for item in pub_sub_sender.listen():
            if isinstance(item["data"], int):
                pass
            else:
                frame_data = json.loads(item["data"])

                # # ACK that this frame has been received
                # key = "resp-%s-%s" % (str(frame_data["drone_id"]), str(frame_data["frame_id"]))
                # print(" @@ # ACK that this frame has been received ... key=", key)
                # redis_set(self.rc_data, key, True, 4)
                # print("VALUE key:", redis_get(self.rc_data, key))

                self.capture_extracted_frame_data(frame_data)
                # print(" --- `Frame Data` has been sent; DATA=", frame_data)
                self.watch_frame_receiver()

    def __is_detection_finished(self):
        status = None
        wait_t0 = time.time()
        while status is None:
            key = "PLF-%d-%d" % (self.drone_id, self.frame_id)
            status = redis_get(self.rc_data, key)
            elapsed_time = (time.time() - wait_t0) * 1000  # in ms

            # print(" ----> status [frame_id=%s]:" % str(self.frame_id), status,
            #       "; elapsed_time: (%.2f)" % elapsed_time)
            # Bug fixed: Unable to receive any result from the expected worker node.
            # mark as no response from YOLOv3 network and ignore BBox info in this particular frame
            if elapsed_time > common_settings["plf_config"]["waiting_limit"]:
                # print(" ----> status [frame_id=%s]:" % str(self.frame_id), status,
                #       "; elapsed_time: (%.2f)" % elapsed_time)
                status = False
                break

            if status is None:
                continue
        return status
        # is_detection_finished = False
        # pub_sub_sender = self.rc.pubsub()
        # pub_sub_sender.subscribe([plf_detection_channel])
        # for item in pub_sub_sender.listen():
        #     if isinstance(item["data"], int):
        #         pass
        #     else:
        #         is_detection_finished = True
        #         break
        # return is_detection_finished

    # Send by: `video_streamer.py`
    def watch_frame_receiver(self):
        try:
            _, self.raw_image = self.frame_receiver.recv_image()
            # print(" --- `Frame Data` has been successfully received: ")
            detection_status = self.__is_detection_finished()
            # if self.__is_detection_finished():
            if detection_status:
                self.process_pih2image()
                # print(" --- `Received Frame` data has been successfully processed & Plotted;")
                self.send_to_visualizer()
            elif detection_status is not None and not detection_status:  # send raw frame without any BBox
                self.send_to_visualizer()
        except Exception as e:
            print("\t\tRetrieve frame-%d ERROR:" % self.frame_id, e)

    def send_to_visualizer(self):
        # print("~~~ \t This class is expected to send image (TCP) into GUI (main_visualizer.py)")
        this_visualizer_status_channel = "visualizer-status-" + str(self.drone_id)

        t0_sender = time.time()
        idx_vsender = self.drone_id - 1
        self.visual_sender[idx_vsender].send_image(str(self.frame_id), self.plotted_img)
        t_recv = time.time() - t0_sender
        # print('Latency [Send Plotted Frame into Visualizer] of frame-%s: (%.5fs)' % (str(self.frame_id), t_recv))

        if self.opt.enable_cv_out:
            data = {
                "ts": time.time(),
                "drone_id": self.drone_id,
                "frame_id": self.frame_id
            }
            p_mdata = json.dumps(data)
            pub(self.rc_data, this_visualizer_status_channel, p_mdata)  # confirm PLF that frame-n has been sent
        # print('\t[PUBLISH Plotted Frame-%d into Visualizer]' % self.frame_id)

    def process_pih2image(self):
        t0_pihlocfet = time.time()
        pih_gen = PIHLocationFetcher(self.opt, self.raw_image, self.drone_id, self.frame_id, self.raw_image,
                                     self.visual_type)
        pih_gen.run()
        self.bbox = pih_gen.get_bbox()
        self.mbbox = pih_gen.get_mbbox()
        self.plotted_img = pih_gen.get_mbbox_img()
        t_pihlocfet = time.time() - t0_pihlocfet
        # print("Latency [PiH Location Fetcher] of frame-%d: (%.5fs)" % (self.frame_id, t_pihlocfet))
