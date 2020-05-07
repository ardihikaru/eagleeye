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
        # self.plf_sender_channel = "plf-sender"
        self.plf_send_status_channel = "plf-send-status"
        # self.plf_frame_receiver_channel_pre = "plf-receiver-frame"
        self.plf_bbox_receiver_channel_pre = "plf-receiver-bbox"
        self.drone_id = None
        self.frame_id = 0
        self.worker_id = None
        self.raw_image = None
        self.plotted_img = None
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
            # self.visual_sender = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
            this_visual_sender = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
            self.visual_sender.append(this_visual_sender)
            # self.visualizer_status_channel = "visualizer-status-" + str(self.drone_id)

        # port = self.opt.visualizer_port_prefix + str(self.drone_id)
        # url = 'tcp://127.0.0.1:' + port
        # self.visual_sender = imagezmq.ImageSender(connect_to=url, REQ_REP=False)
        # self.visualizer_status_channel = "visualizer-status-" + str(self.drone_id)

    # PiH Location Fetcher (plf)
    def __set_plf_receiver(self):
        url = 'tcp://127.0.0.1:' + str(self.opt.pih_location_fetcher_port)
        self.frame_receiver = imagezmq.ImageHub(open_port=url, REQ_REP=False)
        # self.plf_receiver_channel = "plf-sender"

    def run(self):
        self.watch_frame_sender()

    # TBD
    def capture_extracted_frame_data(self, frame_data):
        self.drone_id = frame_data["drone_id"]
        self.frame_id = frame_data["frame_id"]
        self.visual_type = frame_data["visual_type"]
        # self.worker_id = frame_data["worker_id"]

    # Sent by: `video_streamer.py`
    def watch_frame_sender(self):
        pub_sub_sender = self.rc_data.pubsub()
        pub_sub_sender.subscribe([self.plf_send_status_channel])
        for item in pub_sub_sender.listen():
            if isinstance(item["data"], int):
                pass
            else:
                frame_data = json.loads(item["data"])
                self.capture_extracted_frame_data(frame_data)
                print(" --- `Frame Data` has been sent; DATA=", frame_data)
                # print("\tWaiting receiver to give RESPONSE")
                self.watch_frame_receiver()

    def __is_detection_finished(self):
        # print(" ## @ __is_detection_finished")
        plf_detection_channel = "PLF-%d-%d" % (self.drone_id, self.frame_id)
        # print("$$ plf_detection_channel:", plf_detection_channel)
        # detection_result = None
        is_detection_finished = False
        while not is_detection_finished:
            is_detection_finished = redis_get(self.rc_data, plf_detection_channel)
            if is_detection_finished is None:
                is_detection_finished = False
        return is_detection_finished

    # TBD
    # Send by: `video_streamer.py`
    def watch_frame_receiver(self):
        try:
            _, self.raw_image = self.frame_receiver.recv_image()
            # print(" ..... DAPET nih..")
            print(" --- `Frame Data` has been successfully received: ")
            # print("\tWaiting to retrieve BBox and MBBox information")
            # self.watch_bbox_receiver()
            # self.capture_extracted_bbox_data()
            if self.__is_detection_finished():
                self.process_pih2image()
                print(" --- `Received Frame` data has been successfully processed & Plotted;")
                # print(" --- \t BBox info: ", self.bbox)
                # print(" --- \t MBBox info: ", self.mbbox)
                # print(" --- `Received Frame` data has been successfully processed; BBox info: ", bbox_data)
                self.send_to_visualizer()
        except Exception as e:
            print("\t\tRetrieve frame-%d ERROR:" % self.frame_id, e)

    def send_to_visualizer(self):
        print("~~~ \t This class is expected to send image (TCP) into GUI (main_visualizer.py)")
        # self.__set_visual_sender()
        this_visualizer_status_channel = "visualizer-status-" + str(self.drone_id)

        t0_sender = time.time()
        # self.visual_sender.send_image(str(self.frame_id), self.plotted_img)
        idx_vsender = self.drone_id - 1
        self.visual_sender[idx_vsender].send_image(str(self.frame_id), self.plotted_img)
        t_recv = time.time() - t0_sender
        print('Latency [Send Plotted Frame into Visualizer] of frame-%s: (%.5fs)' % (str(self.frame_id), t_recv))

        # print("###### visualizer_status_channel:", self.visualizer_status_channel)
        print("###### visualizer_status_channel:", this_visualizer_status_channel)
        if self.opt.enable_cv_out:
            print("\t ~~~~~ @ if self.opt.enable_cv_out: ....")
            data = {
                "drone_id": self.drone_id,
                "frame_id": self.frame_id
                # "visual_type": self.visual_type
            }
            print(" \t ---- data:", data)
            p_mdata = json.dumps(data)
            # pub(self.rc_data, self.visualizer_status_channel, p_mdata)  # confirm PLF that frame-n has been sent
            pub(self.rc_data, this_visualizer_status_channel, p_mdata)  # confirm PLF that frame-n has been sent
        print('\t[PUBLISH Plotted Frame-%d into Visualizer]' % self.frame_id)

        # pub_sub_receiver_frame = self.rc_data.pubsub()
        # plf_frame_receiver_status_channel = self.plf_frame_receiver_channel_pre + "-%d-%d" % (self.drone_id, self.frame_id)
        # pub_sub_receiver_frame.subscribe([plf_frame_receiver_status_channel])
        # for item in pub_sub_receiver_frame.listen():
        #     if isinstance(item["data"], int):
        #         pass
        #     else:
        #         frame_data = json.loads(item["data"])
        #         self.raw_image = None  # TBD
        #         print(" --- `Frame Data` has been successfully received: ", frame_data)
        #         print("\tWaiting to retrieve BBox and MBBox information")
        #         self.watch_bbox_receiver()
        #         break
        # print("\tEXITING: Frame Watcher")

    # def __extract_bbox_data(self, prefix):
    #     key_bbox = "d" + str(self.drone_id) + "-f" + str(self.frame_id) + prefix
    #
    #     bbox_data = None
    #     while bbox_data is None:
    #         bbox_data = redis_get(self.rc_bbox, key_bbox)
    #         if bbox_data is None:
    #             continue
    #         else:
    #             bbox_data = json.loads(bbox_data)
    #     return bbox_data
    #
    #     # bbox_data = redis_get(self.rc_bbox, key_bbox)
    #     # bbox_dict = json.loads(bbox_data)
    #     # return bbox_dict
    #
    # # TBD
    # # def capture_extracted_bbox_data(self, bbox_data):
    # def capture_extracted_bbox_data(self):
    #     # self.total_pih_candidates = bbox_data["total_pih_candidates"]
    #     # self.period_pih_candidates = bbox_data["period_pih_candidates"]
    #     # key_bbox = "d" + str(self.drone_id) + "-f" + str(self.frame_id) + "-bbox"
    #     # key_mbbox = "d" + str(self.drone_id) + "-f" + str(self.frame_id) + "-mbbox"
    #     self.bbox = self.__extract_bbox_data("-bbox")
    #     self.mbbox = self.__extract_bbox_data("-bbox")
    #     # self.mbbox = bbox_data["mbbox"]

    # # TBD
    # # Send by: `yolo_v3.py`
    # def watch_bbox_receiver(self):
    #     pub_sub_receiver_bbox = self.rc_data.pubsub()
    #     plf_bbox_receiver_status_channel = self.plf_bbox_receiver_channel_pre + "-%d-%d" % (self.drone_id, self.frame_id)
    #     pub_sub_receiver_bbox.subscribe([plf_bbox_receiver_status_channel])
    #     for item in pub_sub_receiver_bbox.listen():
    #         if isinstance(item["data"], int):
    #             pass
    #         else:
    #             bbox_data = json.loads(item["data"])
    #             self.capture_extracted_bbox_data(bbox_data)
    #             print(" --- `Received Frame` data has been successfully processed; BBox info: ", bbox_data)
    #             self.process_pih2image()
    #             break
    #     print("\tEXITING: BBox Watcher")

    # TBD
    def process_pih2image(self):
        t0_pihlocfet = time.time()
        # pih_gen = PIHLocationFetcher(self.opt, self.raw_image, self.frame_id)
        pih_gen = PIHLocationFetcher(self.opt, self.raw_image, self.drone_id, self.frame_id, self.raw_image,
                                     self.visual_type)
        # pih_gen = PIHLocationFetcher(self.opt, self.raw_image, self.frame_id, self.total_pih_candidates,
        #                              self.period_pih_candidates)
        pih_gen.run()
        self.bbox = pih_gen.get_bbox()
        self.mbbox = pih_gen.get_mbbox()
        self.plotted_img = pih_gen.get_mbbox_img()
        # self.total_pih_candidates = pih_gen.get_total_pih_candidates()
        # self.period_pih_candidates = pih_gen.get_period_pih_candidates()
        t_pihlocfet = time.time() - t0_pihlocfet
        print("Latency [PiH Location Fetcher] of frame-%d: (%.5fs)" % (self.frame_id, t_pihlocfet))
