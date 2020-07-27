from utils.utils import *
import matplotlib.patches as mpatches
from libs.addons.redis.my_redis import MyRedis
from libs.addons.redis.translator import redis_get, redis_set
import argparse

class PlotE2E:
    def __init__(self, opt):
        self.opt = opt
        # self.to_ms = opt.to_ms
        self.latency_output = opt.output_graph
        # # self.latency_output = opt.output_graph
        # redis = MyRedis()
        # self.rc = redis.get_rc()
        # self.rc_gps = redis.get_rc_gps()
        # self.rc_latency = redis.get_rc_latency()

    def run(self):
        self.end2end_latency_graph()

    # def autolabel(self, rects):
    #     """Attach a text label above each bar in *rects*, displaying its height."""
    #     for rect in rects:
    #         height = rect.get_height()
    #         ax.annotate('{}'.format(height),
    #                     xy=(rect.get_x() + rect.get_width() / 2, height),
    #                     xytext=(0, 3),  # 3 points vertical offset
    #                     textcoords="offset points",
    #                     ha='center', va='bottom')

    def end2end_latency_graph(self):
        # 1 worker, 3 workers, 5 workers
        e2e_latency = [
            24.52103,
            13.53070,
            11.40873
        ]

        # Define number of iteration (K)
        K = len(e2e_latency)
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        plt.style.use('ggplot')

        x_info = ['1', '3', '5']

        plt.bar(ks, e2e_latency, color='green')
        plt.xlabel("Number of workers")
        plt.ylabel("Latency (ms)")
        plt.title("End-to-end Latency")

        plt.xticks(ks, x_info)

        plt.show()
        fig.savefig(self.latency_output + 'end2end_comparison.png', dpi=fig.dpi)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--to_ms', type=bool, default=True, help='Convert (from seconds) into miliseconds')
    parser.add_argument('--drone_id', type=int, default=1, help='Drone ID')
    parser.add_argument("--output_graph", type=str, default="output_graph/", help="path to save graph")
    opt = parser.parse_args()
    print(opt)

    PlotE2E(opt).run()
