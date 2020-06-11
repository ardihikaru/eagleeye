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


class ExportLatency:
    def __init__(self, opt):
        self.read2stream = []
        self.sub2frame = []
        self.yolo_load_img = []
        self.yolo_inference = []
        self.yolo_nms = []
        self.yolo_modv1 = []
        self.yolo_modv2 = []
        self.visualizer_fps = []
        self.visualizer_lat = []
        self.lb_fps = []
        self.worker_fps = []
        self.opt = opt
        self.to_ms = opt.to_ms
        self.latency_output = opt.output_csv
        redis = MyRedis()
        self.rc = redis.get_rc()
        self.rc_gps = redis.get_rc_gps()
        self.rc_latency = redis.get_rc_latency()

        self.set_last_frame_id()
        self.num_frames = self.last_frame_id

        self.__init_csv_folder()

    def __init_csv_folder(self):
        csv_path = self.latency_output + str(self.opt.num_workers) + "/"

        if os.path.exists(csv_path):
            shutil.rmtree(csv_path)  # delete output folder
        os.makedirs(csv_path)  # make new output folder

    def set_last_frame_id(self):
        key = "last-" + str(self.opt.drone_id)
        self.last_frame_id = redis_get(self.rc_latency, key)

        # Bug fixing: simply ignore last frame
        # self.last_frame_id = self.last_frame_id - 1

    # @`reading_video.py`
    def get_read_stream_latency(self):
        for idx in range (1, (self.num_frames+1)):
            key = "frame-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)

            if value is not None:
                if self.to_ms:
                    value = value * 1000

                    # Add end-to-end latency
                    if self.opt.enable_e2e:
                        value += self.opt.avg_frame

                self.read2stream.append(value)

        self.save_to_csv('01_read_stream_latency-w=%d.csv' % self.opt.num_workers, self.read2stream)  # X is an array

    # # @`worker_yolov3.py`
    # def get_sub2frame_latency(self):
    #     for idx in range (1, (self.num_frames+1)):
    #         key = "sub2frame-" + str(self.opt.drone_id) + "-" + str(idx)
    #         value = redis_get(self.rc_latency, key)
    #         if self.to_ms:
    #             value = value * 1000
    #         self.sub2frame.append(value)
    #
    #     self.save_to_csv('02_sub2frame_latency-w=%d.csv' % self.opt.num_workers, self.sub2frame)  # X is an array

    # # @`worker_yolov3.py`
    # def get_yolo_load_img_latency(self):
    #     for idx in range (1, (self.num_frames+1)):
    #         key = "loadIMG-" + str(self.opt.drone_id) + "-" + str(idx)
    #         value = redis_get(self.rc_latency, key)
    #         if self.to_ms:
    #             value = value * 1000
    #         self.yolo_load_img.append(value)
    #
    #     self.save_to_csv('03_yolo_load_img_latency-w=%d.csv' % self.opt.num_workers, self.yolo_load_img)  # X is an array

    # @`worker_yolov3.py`
    def get_yolo_inference_latency(self):
        for idx in range (1, (self.num_frames+1)):
            key = "inference-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if value is not None:
                if self.to_ms:
                    value = value * 1000
                self.yolo_inference.append(value)

        self.save_to_csv('04_yolo_inference_latency-w=%d.csv' % self.opt.num_workers, self.yolo_inference)  # X is an array

    # @`worker_yolov3.py`
    def get_yolo_nms_latency(self):
        for idx in range (1, (self.num_frames+1)):
            key = "nms-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if value is not None:
                if self.to_ms:
                    value = value * 1000
                self.yolo_nms.append(value)

        self.save_to_csv('05_yolo_nms_latency-w=%d.csv' % self.opt.num_workers, self.yolo_nms)  # X is an array

    # @`worker_yolov3.py: Not used anymore`
    def get_yolo_modv1_latency(self):
        for idx in range (1, (self.num_frames+1)):
            key = "modv1-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if value is not None:
                if self.to_ms:
                    value = value * 1000
                self.yolo_modv1.append(value)

        self.save_to_csv('06_yolo_modv1_latency-w=%d.csv' % self.opt.num_workers, self.yolo_modv1)  # X is an array

    # @`worker_yolov3.py: Not used anymore`
    def get_yolo_modv2_latency(self):
        for idx in range (1, (self.num_frames+1)):
            key = "modv2-" + str(self.opt.drone_id) + "-" + str(idx)
            value = redis_get(self.rc_latency, key)
            if value is not None:
                if self.to_ms:
                    value = value * 1000
                self.yolo_modv2.append(value)

        self.save_to_csv('07_yolo_modv2_latency-w=%d.csv' % self.opt.num_workers, self.yolo_modv2)  # X is an array

    def get_visualizer_fps(self):
        for idx in range (1, (self.num_frames+1)):
            key = "fps-visualizer-" + str(self.opt.drone_id)
            value = redis_get(self.rc_latency, key)
            if value is not None:
                self.visualizer_fps.append(value)

        self.save_to_csv('08_visualizer_fps.csv', self.visualizer_fps)  # X is an array

    def get_visualizer_lat(self):
        for idx in range (1, (self.num_frames+1)):
            key = "lat-visualizer-" + str(self.opt.drone_id)
            value = redis_get(self.rc_latency, key)
            if value is not None:
                self.visualizer_lat.append(value)

        self.save_to_csv('08-2_visualizer_lat.csv', self.visualizer_fps)  # X is an array

    def get_load_balancer_fps(self):
        for idx in range (1, (self.num_frames+1)):
            key = "fps-load-balancer-" + str(self.opt.drone_id)
            value = redis_get(self.rc_latency, key)
            if value is not None:
                self.lb_fps.append(value)

        self.save_to_csv('08_load_balancer_fps.csv', self.lb_fps)  # X is an array

    def get_worker_fps(self):
        for i in range(self.opt.num_workers):
            worker_id = i + 1

            self.worker_fps = []
            for idx in range (1, (self.num_frames+1)):
                key = "fps-load-balancer-" + str(self.opt.drone_id)
                value = redis_get(self.rc_latency, key)
                if value is not None:
                    self.worker_fps.append(value)

            self.save_to_csv('09_[w=%d]_worker_fps.csv' % worker_id, self.worker_fps)

    def load_data(self):
        # @`reading_video.py`
        self.get_read_stream_latency()

        # @`worker_yolov3.py`
        # self.get_sub2frame_latency()
        # self.get_yolo_load_img_latency()
        self.get_yolo_inference_latency()
        self.get_yolo_nms_latency()

        # self.get_yolo_modv1_latency()
        self.get_yolo_modv2_latency()

        # New latency measurement in EagleEYE_v2
        self.get_visualizer_fps()
        self.get_visualizer_lat()
        self.get_load_balancer_fps()
        self.get_worker_fps()

    def run(self):
        self.load_data()

        # to smooth the graph
        # self.discard_frame_one()

    def save_to_csv(self, fname, data):
        save_path = self.latency_output + str(self.opt.num_workers) + "/" + fname
        np.savetxt(save_path, data, delimiter=',')  # X is an array

    def read_data(self, fname):
        fpath = self.latency_output + fname
        with open(fpath, 'r') as f:
            reader = csv.reader(f)
            return [float(line[0]) for line in list(reader)]

    # def discard_frame_one(self):
    #     del self.read2stream[0]
    #     del self.sub2frame[0]
    #
    #     del self.yolo_load_img[0]
    #     del self.yolo_inference[0]
    #     del self.yolo_nms[0]
    #
    #     self.num_frames = self.num_frames - 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sum_total', type=int, default=6, help='Number of workers')
    parser.add_argument('--num_workers', type=int, default=1, help='Number of workers')
    parser.add_argument('--enable_e2e', type=bool, default=False, help='Enable End-to-end calculation') # `value` += `avg_frame`
    parser.add_argument('--to_ms', type=bool, default=True, help='Convert value (from seconds) into miliseconds')
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument("--output_csv", type=str, default="exported_data/csv/", help="path to save the exported csv files")
    opt = parser.parse_args()
    # print(opt)

    ExportLatency(opt).run()
