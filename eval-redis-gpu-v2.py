from utils.utils import *
import matplotlib.patches as mpatches
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_get, redis_set
import argparse

# latency_output = "saved_latency"

'''
List of Latency Measurements:
    @`reading_video.py`: 
        1. Stream Start Time (CV Capture)               : stream-start-<droneID>-<frameID>
        2. Reading stream frame (CV Read)               : frame-<droneID>-<frameID>
        3. Saving image to (shared) disk                : f2disk-<droneID>-<frameID> 
        4. Publish frame information to worker YOLOv3   : pub2frame-<droneID>-<frameID>  

    @`worker_yolov3.py`:
        1. Subscribing frame (from other container)     : sub2frame-<droneID>-<frameID>
        2. Loading image into YOLOv3 Worker             : loadIMG-<droneID>-<frameID>
        3. Performing Inference                         : inference-<droneID>-<frameID>
        4. Performing Non-Maximum Suppression (NMS)     : nms-<droneID>-<frameID>
        5. Performing MB-Box Algorithm                  : mbbox-<droneID>-<frameID>
        6. Performing Default Detection (drawing bbox)  : draw2bbox-<droneID>-<frameID>
        7. End-to-end each frame                        : end2end-frame-<droneID>-<frameID>
        8. End-to-end each TOTAL                        : end2end-<droneID>
        
Other Latency @`worker_yolov3.py`:
    1. Load weight                                      : weight-<droneID>-<frameID> 
    2. Load eval. model                                 : evalModel-<droneID>-<frameID> 
    
Other IMPORTANT Keys @`worker_yolov3.py`:
    1. Marked last processed frame                      : last-<droneID> 
'''

class Plot:
    def __init__(self, opt):
        self.opt = opt
        self.to_ms = opt.to_ms
        self.latency_output = opt.output_graph
        # self.latency_output = opt.output_graph
        redis = MyRedis()
        self.rc = redis.get_rc()
        self.rc_gps = redis.get_rc_gps()
        self.rc_latency = redis.get_rc_latency()

        self.set_last_frame_id()
        # self.num_frames = self.last_frame_id + 1
        self.num_frames = self.last_frame_id

        # self.total_frames = 10

        # print(" Current Keys = ", self.rc_latency.keys())
        # print(" >>> last Frame Number = ", self.last_frame_id)

        # self.latency_output = "saved_latency"
        # self.sub_path = "/comparison-gpu/custom"
        # self.csv_inference = "time_inference_latency.csv"
        # self.csv_nms = "time_nms_latency.csv"
        # self.csv_mbbox = "time_mbbox_latency.csv"
        # self.csv_default = "time_bbox_latency.csv"

    def set_last_frame_id(self):
        key = "last-" + str(self.opt.drone_id)
        self.last_frame_id = redis_get(self.rc_latency, key)

        # Bug fixing: simply ignore last frame
        # self.last_frame_id = self.last_frame_id - 1

    # @`reading_video.py`
    def get_stream_setup_latency(self):
        key = "stream-start-" + str(self.opt.drone_id)
        value = redis_get(self.rc_latency, key)
        # print("# Key, value = ", value)
        if self.to_ms:
            value = value * 1000
        self.stream_setup = value

        self.save_to_csv('01_stream_setup_latency-w=%d.csv' % self.opt.num_workers, [self.stream_setup])  # X is an array

    # @`reading_video.py`
    def get_read_stream_latency(self):
        self.read2stream = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "frame-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)

            if self.to_ms:
                value = value * 1000

                # Add end-to-end latency
                if self.opt.enable_e2e:
                    value += self.opt.avg_frame

            # print("# Key[`%s`], value = " % key, value)
            self.read2stream.append(value)

        self.save_to_csv('02_read_stream_latency-w=%d.csv' % self.opt.num_workers, self.read2stream)  # X is an array

    # @`reading_video.py`
    def get_frame2disk_latency(self):
        self.frame2disk = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "f2disk-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.frame2disk.append(value)

        self.save_to_csv('03_frame2disk_latency-w=%d.csv' % self.opt.num_workers, self.frame2disk)  # X is an array

    # @`reading_video.py`
    def get_pub2frame_latency(self):
        self.pub2frame = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "pub2frame-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.pub2frame.append(value)

        self.save_to_csv('04_pub2frame_latency-w=%d.csv' % self.opt.num_workers, self.pub2frame)  # X is an array

    # @`worker_yolov3.py`
    def get_sub2frame_latency(self):
        self.sub2frame = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "sub2frame-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.sub2frame.append(value)

        self.save_to_csv('05_sub2frame_latency-w=%d.csv' % self.opt.num_workers, self.sub2frame)  # X is an array

    # @`worker_yolov3.py`
    def get_yolo_load_img_latency(self):
        self.yolo_load_img = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "loadIMG-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.yolo_load_img.append(value)

        self.save_to_csv('06_yolo_load_img_latency-w=%d.csv' % self.opt.num_workers, self.yolo_load_img)  # X is an array

    # @`worker_yolov3.py`
    def get_yolo_inference_latency(self):
        self.yolo_inference = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "inference-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.yolo_inference.append(value)

        self.save_to_csv('07_yolo_inference_latency-w=%d.csv' % self.opt.num_workers, self.yolo_inference)  # X is an array

    # @`worker_yolov3.py`
    def get_yolo_nms_latency(self):
        self.yolo_nms = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "nms-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.yolo_nms.append(value)

        self.save_to_csv('08_yolo_nms_latency-w=%d.csv' % self.opt.num_workers, self.yolo_nms)  # X is an array

    # @`worker_yolov3.py: Not used anymore`
    def get_yolo_mbbox_latency(self):
        self.yolo_mbbox = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "mbbox-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.yolo_mbbox.append(value)

        self.save_to_csv('09_yolo_mbbox_latency-w=%d.csv' % self.opt.num_workers, self.yolo_mbbox)  # X is an array

    # @`worker_yolov3.py`
    def get_yolo_draw_bbox_latency(self):
        self.yolo_draw_bbox = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "draw2bbox-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.yolo_draw_bbox.append(value)

        self.save_to_csv('10_yolo_draw_bbox_latency-w=%d.csv' % self.opt.num_workers, self.yolo_draw_bbox)  # X is an array

    # @`worker_yolov3.py`
    def get_end2end_frame_latency(self):
        self.end2end_frame = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "end2end-frame-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.end2end_frame.append(value)

        self.save_to_csv('11_end2end_frame_latency-w=%d.csv' % self.opt.num_workers, self.end2end_frame)  # X is an array

    # @`worker_yolov3.py`
    def get_end2end_latency(self):
        key = "end2end-" + str(self.opt.drone_id)
        value = redis_get(self.rc_latency, key)
        # print("# Key, value = ", value)
        # if self.to_ms:
        #     value = value * 1000
        self.end2end = value

        self.save_to_csv('12_end2end_latency-w=%d.csv' % self.opt.num_workers, [self.end2end])  # X is an array

    # @`worker_yolov3.py: Not used anymore`
    def get_yolo_modv1_latency(self):
        self.yolo_modv1 = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "modv1-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.yolo_modv1.append(value)

        self.save_to_csv('13_yolo_modv1_latency-w=%d.csv' % self.opt.num_workers, self.yolo_modv1)  # X is an array

    # @`worker_yolov3.py: Not used anymore`
    def get_yolo_modv2_latency(self):
        self.yolo_modv2 = []
        # for idx in range (1, self.num_frames):
        for idx in range (1, (self.num_frames+1)):
            key = "modv2-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if self.to_ms:
                value = value * 1000
            # print("# Key[`%s`], value = " % key, value)
            self.yolo_modv2.append(value)

        self.save_to_csv('14_yolo_modv2_latency-w=%d.csv' % self.opt.num_workers, self.yolo_modv2)  # X is an array

    def load_data(self):
        # @`reading_video.py`
        self.get_stream_setup_latency()
        self.get_read_stream_latency()
        self.get_frame2disk_latency()
        self.get_pub2frame_latency()

        # @`worker_yolov3.py`
        self.get_sub2frame_latency()
        self.get_yolo_load_img_latency()
        self.get_yolo_inference_latency()
        self.get_yolo_nms_latency()
        self.get_yolo_mbbox_latency()
        self.get_yolo_draw_bbox_latency()

        self.get_end2end_frame_latency()
        self.get_end2end_latency()

        self.get_yolo_modv1_latency()
        self.get_yolo_modv2_latency()

    def run(self):
        self.load_data()

        # to smooth the graph
        # self.discard_frame_one()

        self.export_frame_latency()

        self.frame_communication_latency_graph()
        self.frame_processing_latency_graph()

        # not used yet
        # self.end2end_latency_graph()
        # self.end2end_comparison_graph()

    # Due to round robin load balancing
    def calc_w_3(self, frame_id):
        f6 = self.end2end_frame[(frame_id-1)]
        f5 = self.end2end_frame[(frame_id-2)]
        f4 = self.end2end_frame[(frame_id-3)]
        f3 = self.end2end_frame[(frame_id-4)]
        f2 = self.end2end_frame[(frame_id-5)]
        f1 = self.end2end_frame[(frame_id-6)]
        w1 = (f1 + f4)/2
        w2 = (f2 + f5)/2
        w3 = (f3 + f6)/2
        total = w1 + w2 + w3
        return total

    def export_frame_latency(self):
        self.couple_latency = []
        self.total_data_points = 0
        tmp_total = 0
        for frame_id in range(1, (self.num_frames+1)):
            tmp_total += self.end2end_frame[(frame_id-1)]
            if frame_id % self.opt.sum_total == 0:
                if self.opt.num_workers == 1:
                    self.couple_latency.append(tmp_total)
                elif self.opt.num_workers == 3:
                    total = self.calc_w_3(frame_id)
                    self.couple_latency.append(total)
                elif self.opt.num_workers == 6:
                    total = tmp_total / 6
                    self.couple_latency.append(total)
                tmp_total = 0
                self.total_data_points += 1

        # print("\nFrom %d data, Collecting %d data points." % (len(self.end2end_frame), len(self.couple_latency)))
        self.save_to_csv('sum-latency-w=%d.csv' % self.opt.num_workers, self.couple_latency)  # X is an array

    def save_to_csv(self, fname, data):
        np.savetxt(self.latency_output + fname, data, delimiter=',')  # X is an array

    def read_data(self, fname):
        fpath = self.latency_output + fname
        with open(fpath, 'r') as f:
            reader = csv.reader(f)
            return [float(line[0]) for line in list(reader)]

    def discard_frame_one(self):
        del self.read2stream[0]
        del self.frame2disk[0]
        del self.pub2frame[0]
        del self.sub2frame[0]

        del self.yolo_load_img[0]
        del self.yolo_inference[0]
        del self.yolo_nms[0]
        del self.yolo_mbbox[0]

        del self.end2end_frame[0]

        self.num_frames = self.num_frames - 1

    def frame_communication_latency_graph(self):
        # Define number of iteration (K)
        K = self.num_frames
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        title = "Communication Latency"
        plt.title(title)
        # plt.plot(ks, self.read2stream, label='Per Frame Streaming')
        # plt.plot(ks, self.read2stream, label='Frame acquisition')
        plt.plot(ks, self.read2stream, label='Frame capture')
        # plt.plot(ks, self.frame2disk, label='Save frame to disk')
        plt.plot(ks, self.frame2disk, label='Frame storing')
        # plt.plot(ks, self.pub2frame, label='Frame publication')
        # plt.plot(ks, self.sub2frame, label='Frame Subscription')
        plt.xlabel('Frame Number')
        plt.ylabel('Latency (ms)')
        plt.legend()
        plt.show()
        # print("##### Saving graph into: ", self.latency_output + 'communication_latency_per_frame.png')
        fig.savefig(self.latency_output + 'communication_latency_per_frame-w=%d.png' % self.opt.num_workers, dpi=fig.dpi)

    def frame_processing_latency_graph(self):
        # Define number of iteration (K)
        K = self.num_frames
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        title = "Processing Latency"
        plt.title(title)
        # plt.plot(ks, self.yolo_load_img, label='Image Retrieval')
        plt.plot(ks, self.yolo_load_img, label='Image Loading')
        plt.plot(ks, self.yolo_inference, label='Inference')
        plt.plot(ks, self.yolo_nms, label='NMS')
        plt.plot(ks, self.yolo_mbbox, label='MB-Box')
        # plt.plot(ks, self.yolo_draw_bbox, label='Draw Normal B-Box Latency')
        plt.xlabel('Frame Number')
        plt.ylabel('Latency (ms)')
        plt.legend()
        plt.show()
        # print("##### Saving graph into: ", self.latency_output + 'processing_latency_per_frame.png')
        fig.savefig(self.latency_output + 'processing_latency_per_frame-w=%d.png' % self.opt.num_workers, dpi=fig.dpi)

    def end2end_comparison_graph(self):

        worker1, worker2, worker3 = None, None, None
        try:
            worker1 = self.read_data('sum-latency-w=1.csv')
            worker2 = self.read_data('sum-latency-w=3.csv')
            worker3 = self.read_data('sum-latency-w=6.csv')
        except:
            pass

        if worker1 is not None and worker2 is not None and worker3 is not None:
            del worker1[0]
            del worker2[0]
            del worker3[0]

            # Define number of iteration (K)
            # K = self.total_data_points
            K = len(worker1)
            ks = int_to_tuple(K)  # used to plot the results

            print("LEN worker1:", len(worker1))
            print("LEN worker2:", len(worker2))
            print("LEN worker3:", len(worker3))

            fig = plt.figure()
            title = "Comparison of Pattern Recognition Latency"
            plt.title(title)
            plt.plot(ks, worker1, label='1 Worker')
            plt.plot(ks, worker2, label='3 Workers')
            plt.plot(ks, worker3, label='6 Workers')
            plt.xlabel('Frame Batch Number')
            plt.ylabel('Latency (ms)')
            plt.legend()

            # x_info = [str(i) for i in range(1, K + 1)]
            # plt.xticks(ks, x_info)

            plt.show()
            # print("##### Saving graph into: ", self.latency_output + 'end2end_latency_per_frame.png')
            fig.savefig(self.latency_output + 'PR_latency_comparison.png', dpi=fig.dpi)

    def end2end_latency_graph(self):
        # Define number of iteration (K)
        K = self.num_frames
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        title = "Pattern Recognition (PR) Latency"
        plt.title(title)
        plt.plot(ks, self.end2end_frame, label='%d Worker' % self.opt.num_workers)
        plt.xlabel('Frame Number')
        plt.ylabel('Latency (ms)')
        plt.legend()

        # x_info = [str(i) for i in range(1, K+1)]
        # plt.xticks(ks, x_info)

        plt.show()
        # print("##### Saving graph into: ", self.latency_output + 'end2end_latency_per_frame.png')
        fig.savefig(self.latency_output + 'end2end_latency_per_frame.png', dpi=fig.dpi)

    def calculate_e2e(self):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sum_total', type=int, default=6, help='Number of workers')
    parser.add_argument('--num_workers', type=int, default=1, help='Number of workers')
    parser.add_argument('--timestamp', type=float, default=1580798146.107, help='AVG frame of the Drone (s)') # $ date +%s%3N
    parser.add_argument('--avg_frame', type=float, default=2.2, help='Average frame latency from the Drone (ms)')
    # parser.add_argument('--enable_e2e', type=bool, default=True, help='Enable End-to-end calculation') # `value` += `avg_frame`
    parser.add_argument('--enable_e2e', type=bool, default=False, help='Enable End-to-end calculation') # `value` += `avg_frame`
    parser.add_argument('--to_ms', type=bool, default=True, help='Convert value (from seconds) into miliseconds')
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    # parser.add_argument("--output_graph", type=str, default="output_graph/", help="path to save the graphs")
    parser.add_argument("--output_graph", type=str, default="/media/ramdisk/output_graph/", help="path to save the graphs")
    opt = parser.parse_args()
    print(opt)

    Plot(opt).run()
