from utils.utils import *
from libs.addons.redis.my_redis import MyRedis
import argparse

class Plot:
    def __init__(self, opt):
        self.read2stream = []
        self.sub2frame = []
        self.yolo_load_img = []
        self.yolo_inference = []
        self.yolo_nms = []
        self.yolo_modv1 = []
        self.yolo_modv2 = []
        self.visualizer_fps = []
        self.lb_fps = []
        self.worker_fps = []
        self.opt = opt
        self.latency_output = opt.output_graph
        redis = MyRedis()
        self.rc = redis.get_rc()
        self.rc_gps = redis.get_rc_gps()
        self.rc_latency = redis.get_rc_latency()

        self.__init_plot_folder()

    def __init_plot_folder(self):
        if os.path.exists(self.latency_output):
            shutil.rmtree(self.latency_output)  # delete output folder
        os.makedirs(self.latency_output)  # make new output folder

    def extract_latency_data(self, drone_id):
        data = self.read_data('08_visualizer_fps.csv', drone_id)

        this_latency = []
        for i in range (len(data)):
            total_ms = data[i]
            this_latency.append(total_ms)

        return this_latency

    def __get_drone_ids(self):
        ids = []
        for i in range(self.opt.num_drones):
            drone_id = str((i+1))
            ids.append(drone_id)
        return tuple(ids)

    def __get_latency_data(self):
        data = []
        for i in range(self.opt.num_drones):
            drone_id = str(i+1)
            lat_data = self.extract_latency_data(drone_id)
            mean_lat_data = round(np.mean(np.array(lat_data)), 2)
            data.append(mean_lat_data)
        return data

    def visualizer_latency_graph(self):
        fig = plt.figure()
        title = "Average FPS; #Drones=%s" % str(self.opt.num_drones)
        plt.title(title)

        drones_ids = self.__get_drone_ids()
        y_pos = np.arange(len(drones_ids))
        avg_latency_data = self.__get_latency_data()

        plt.bar(y_pos, avg_latency_data, align='center', alpha=0.5)
        plt.xticks(y_pos, drones_ids)
        plt.ylabel('Frame per Second (s)')

        plt.show()
        fig.savefig(self.latency_output + 'Visualizer_latency_#Dr=%d.pdf' % self.opt.num_drones, dpi=fig.dpi)

    def run(self):
        self.visualizer_latency_graph()

        # to smooth the graph
        # self.discard_frame_one()

    def read_data(self, fname, drone_id):
        fpath = self.latency_output + drone_id + "/" + fname
        csv_path = fpath.replace("plot", "csv")
        with open(csv_path, 'r') as f:
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
    parser.add_argument('--num_drones', type=int, default=2, help='Number of Drones')
    parser.add_argument("--output_graph", type=str, default="hasil/media/ramdisk/plot/", help="path to save the graphs")
    opt = parser.parse_args()
    print(opt)

    Plot(opt).run()
