from utils.utils import *
import matplotlib.patches as mpatches
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_get, redis_set
import argparse

class PlotE2E:
    def __init__(self, opt):
        self.opt = opt
        # self.latency_output = opt.output_graph + "mod-analysis/2020-03-19/"
        self.latency_output = opt.output_graph + "modv2/v2_tm04_2/"

    def run(self):
        # self.plot_all()
        self.plot_modv2()

    def plot_modv2(self):
        modv2_fname = "14_yolo_modv2_latency-w=1.csv"
        modv2_latency = read_data(self.latency_output, modv2_fname)

        mean_modv2 = round(np.mean(np.array(modv2_latency)), 2)
        print(mean_modv2)

        # Define number of iteration (K)
        K = len(modv2_latency)
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()

        title = "Processing Latency of MODv2 Algorithm"
        plt.title(title)

        plt.plot(ks, modv2_latency, color='green', label='MODv2')

        plt.axhline(mean_modv2, color='green', linestyle='dashed', linewidth=1, label='AVG MODv2 (%s ms)' % str(mean_modv2))

        plt.xlabel('Frame Number of NCTU Custom Testing Dataset (57 frames total)')
        plt.ylabel('Latency (ms)')
        plt.legend()
        plt.show()

        plt.show()
        fig.savefig(self.latency_output + 'mod-analysis-modv2.png', dpi=fig.dpi)

    def plot_all(self):
        modv1_fname = "13_yolo_modv1_latency-w=1.csv"
        modv2_fname = "14_yolo_modv2_latency-w=1.csv"
        modv1_latency = read_data(self.latency_output, modv1_fname)
        modv2_latency = read_data(self.latency_output, modv2_fname)

        mean_modv1 = round(np.mean(np.array(modv1_latency)), 2)
        mean_modv2 = round(np.mean(np.array(modv2_latency)), 2)

        # Define number of iteration (K)
        K = len(modv1_latency)
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()

        title = "Processing Latency of MOD Algorithm"
        plt.title(title)

        plt.plot(ks, modv1_latency, color='blue', label='MODv1')
        plt.plot(ks, modv2_latency, color='green', label='MODv2')

        plt.axhline(mean_modv1, color='blue', linestyle='dashed', linewidth=1, label='AVG MODv1 (%s ms)' % str(mean_modv1))
        plt.axhline(mean_modv2, color='green', linestyle='dashed', linewidth=1, label='AVG MODv2 (%s ms)' % str(mean_modv2))

        plt.xlabel('Frame Number of NCTU Custom Testing Dataset (57 frames total)')
        plt.ylabel('Latency (ms)')
        plt.legend()
        plt.show()

        plt.show()
        fig.savefig(self.latency_output + 'mod-analysis-all.png', dpi=fig.dpi)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_graph", type=str, default="output_graph/", help="path to save graph")
    opt = parser.parse_args()
    print(opt)

    PlotE2E(opt).run()
