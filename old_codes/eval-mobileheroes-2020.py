from utils.utils import *
# import matplotlib.pyplot as plt
# import numpy as np
# import csv
import matplotlib.patches as mpatches
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_get, redis_set
import argparse

# def int_to_tuple(Ks):
#     lst = []
#     for i in range(Ks):
#         lst.append((i+1))
#     return tuple(lst)

class Plot:
    def __init__(self, opt):
        self.opt = opt
        self.latency_output = opt.csv_data
        redis = MyRedis()
        self.rc = redis.get_rc()
        self.rc_gps = redis.get_rc_gps()
        self.rc_latency = redis.get_rc_latency()

    def run(self):
        fps1, lat1 = self.extract_latency_data("1")
        fps2, lat2 = self.extract_latency_data("2")
        fps3, lat3 = self.extract_latency_data("3")
        fps4, lat4 = self.extract_latency_data("4")
        fps5, lat5 = self.extract_latency_data("5")
        fps6, lat6 = self.extract_latency_data("6")

        self.plot_graph([
            {"fps": fps1, "lat": lat1},
            {"fps": fps2, "lat": lat2},
            {"fps": fps3, "lat": lat3},
            {"fps": fps4, "lat": lat4},
            {"fps": fps5, "lat": lat5},
            {"fps": fps6, "lat": lat6}
        ])

    def extract_latency_data(self, num_worker):
        fps_data = self.read_data('worker=%s/06_visualizer_fps.csv' % num_worker)
        lat_data = self.read_data('worker=%s/07_visualizer_lat.csv' % num_worker)

        this_fps = []
        this_latency = []
        for i in range (len(fps_data)):
            total_ms_fps = fps_data[i]
            total_ms_lat = lat_data[i]
            this_fps.append(total_ms_fps)
            this_latency.append(total_ms_lat)

        return this_fps, this_latency

    def read_data(self, fname):
        fpath = self.latency_output + fname
        with open(fpath, 'r') as f:
            reader = csv.reader(f)
            return [float(line[0]) for line in list(reader)]

    def plot_graph(self, data=None):

        num_data = 1000
        data[0]["fps"] = data[0]["fps"][-num_data:]
        data[0]["lat"] = data[0]["lat"][-num_data:]
        data[1]["fps"] = data[1]["fps"][-num_data:]
        data[1]["lat"] = data[1]["lat"][-num_data:]
        data[5]["fps"] = data[5]["fps"][-num_data:]
        data[5]["lat"] = data[5]["lat"][-num_data:]
        # print(">>> worker=1 LEN FPS:", len(data[0]["fps"]))
        # print(">>> worker=1 LEN LAT:", len(data[0]["lat"]))
        # print(">>> worker=2 LEN FPS:", len(data[1]["fps"]))
        # print(">>> worker=2 LEN LAT:", len(data[1]["lat"]))
        # print(">>> worker=6 LEN FPS:", len(data[2]["fps"]))
        # print(">>> worker=7 LEN LAT:", len(data[2]["lat"]))

        w1_avg_fps = round(np.mean(np.array(data[0]["fps"])), 2)
        w1_avg_lat = round(np.mean(np.array(data[0]["lat"])), 2)
        w2_avg_fps = round(np.mean(np.array(data[1]["fps"])), 2)
        w2_avg_lat = round(np.mean(np.array(data[1]["lat"])), 2)
        w6_avg_fps = round(np.mean(np.array(data[5]["fps"])), 2)
        w6_avg_lat = round(np.mean(np.array(data[5]["lat"])), 2)

        print("[WORKER=1] Avg_FPS=%s; Avg_Lat=%s" % (str(w1_avg_fps), str(w1_avg_lat)))
        print("[WORKER=2] Avg_FPS=%s; Avg_Lat=%s" % (str(w2_avg_fps), str(w2_avg_lat)))
        print("[WORKER=6] Avg_FPS=%s; Avg_Lat=%s" % (str(w6_avg_fps), str(w6_avg_lat)))

        # Define number of iteration (K)
        K = len(data[0]["lat"])
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        title = "Object Detection Latency"
        plt.title(title)
        plt.plot(ks, data[0]["lat"], label='1 Worker')
        plt.plot(ks, data[1]["lat"], label='2 Workers')
        plt.plot(ks, data[5]["lat"], label='6 Workers')

        plt.axhline(w1_avg_lat, color='blue', linestyle='dashed', linewidth=1)
        plt.axhline(w2_avg_lat, color='orange', linestyle='dashed', linewidth=1)
        plt.axhline(w6_avg_lat, color='green', linestyle='dashed', linewidth=1)

        plt.xlabel('Frame ID')
        plt.ylabel('Latency (ms)')
        plt.legend()

        plt.show()
        fig.savefig(self.opt.output_graph + 'object_detection_latency.png', dpi=fig.dpi)
        fig.savefig(self.opt.output_graph + 'object_detection_latency.pdf', dpi=fig.dpi)
        print("saved file into:", self.opt.output_graph + 'PR_latency_comparison_%s.pdf (And .png)')

        # worker1, worker2, worker3 = None, None, None
        # if batch_latency is None:
        #     try:
        #         worker1 = self.read_data('sum-latency-w=1.csv')
        #         worker2 = self.read_data('sum-latency-w=3.csv')
        #         worker3 = self.read_data('sum-latency-w=6.csv')
        #     except:
        #         pass
        # else:
        #     worker1 = batch_latency[0]
        #     worker2 = batch_latency[1]
        #     worker3 = batch_latency[2]
        #
        # if worker1 is not None and worker2 is not None and worker3 is not None:
        #     del worker1[0]
        #     del worker2[0]
        #     del worker3[0]
        #
        #     # Define number of iteration (K)
        #     # K = self.total_data_points
        #     K = len(worker1)
        #     ks = int_to_tuple(K)  # used to plot the results
        #
        #     print("LEN worker1:", len(worker1))
        #     print("LEN worker2:", len(worker2))
        #     print("LEN worker3:", len(worker3))
        #
        #     # print(worker1)
        #
        #     mean_worker1 = round(np.mean(np.array(worker1)), 2)
        #     mean_worker2 = round(np.mean(np.array(worker2)), 2)
        #     mean_worker3 = round(np.mean(np.array(worker3)), 2)
        #
        #     min_worker1 = round(np.min(np.array(worker1)), 2)
        #     min_worker2 = round(np.min(np.array(worker2)), 2)
        #     min_worker3 = round(np.min(np.array(worker3)), 2)
        #
        #     max_worker1 = round(np.max(np.array(worker1)), 2)
        #     max_worker2 = round(np.max(np.array(worker2)), 2)
        #     max_worker3 = round(np.max(np.array(worker3)), 2)
        #
        #     # w1_to_w2 = round(((mean_worker1/mean_worker2)*100), 2)
        #     # w1_to_w3 = round(((mean_worker1/mean_worker3)*100), 2)
        #     # (new - old)/old*100
        #     w1_to_w2 = round(((mean_worker2 - mean_worker1)/mean_worker1*100), 2)
        #     w1_to_w3 = round(((mean_worker3 - mean_worker1)/mean_worker1*100), 2)
        #
        #     print(" >> mean_worker1:", mean_worker1)
        #     print(" >> mean_worker2:", mean_worker2)
        #     print(" >> mean_worker3:", mean_worker3)
        #
        #     print(" >> min_worker1:", min_worker1)
        #     print(" >> min_worker2:", min_worker2)
        #     print(" >> min_worker3:", min_worker3)
        #
        #     print(" >> max_worker1:", max_worker1)
        #     print(" >> max_worker2:", max_worker2)
        #     print(" >> max_worker3:", max_worker3)
        #
        #     print(" >> w1_to_w2:", w1_to_w2, " %")
        #     print(" >> w1_to_w3:", w1_to_w3, " %")
        #
        #
        #     fig = plt.figure()
        #     # title = "Comparison of Pattern Recognition Latency"
        #     title = "Pattern Recognition Latency of TM-04 + %s" % self.opt.mod_version
        #     # title = "Pattern Recognition Latency of TM-06 + %s" % self.opt.mod_version
        #     plt.title(title)
        #     plt.plot(ks, worker1, label='1 Worker')
        #     plt.plot(ks, worker2, label='3 Workers')
        #     plt.plot(ks, worker3, label='6 Workers')
        #
        #     plt.axhline(mean_worker1, color='blue', linestyle='dashed', linewidth=1)
        #     plt.axhline(mean_worker2, color='orange', linestyle='dashed', linewidth=1)
        #     plt.axhline(mean_worker3, color='green', linestyle='dashed', linewidth=1)
        #
        #     plt.xlabel('Frame Batch Number (6 Frames / Batch)')
        #     plt.ylabel('Latency (ms)')
        #     plt.legend()
        #
        #     # x_info = [str(i) for i in range(1, K + 1)]
        #     # plt.xticks(ks, x_info)
        #
        #     plt.show()
        #     print("##### Saving graph into: ", self.latency_output + 'end2end_latency_per_frame.png')
        #     # fig.savefig(self.latency_output + 'PR_latency_comparison_%s.png' % self.opt.mod_version, dpi=fig.dpi)
        #     fig.savefig(self.latency_output + 'PR_latency_comparison_%s.pdf' % self.opt.mod_version, dpi=fig.dpi)
        #     print("saved file into:", self.latency_output + 'PR_latency_comparison_%s.pdf')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mod_version', type=str, default="MOD", help="Version of MOD used in this plot")
    parser.add_argument("--csv_data", type=str, default="exported_data/csv/", help="path to save the graphs")
    parser.add_argument("--output_graph", type=str, default="output_graph/mobileheroes2020/", help="path to save the graphs")
    opt = parser.parse_args()
    print(opt)

    Plot(opt).run()

