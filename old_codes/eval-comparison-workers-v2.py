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
        self.latency_output = opt.output_graph
        redis = MyRedis()
        self.rc = redis.get_rc()
        self.rc_gps = redis.get_rc_gps()
        self.rc_latency = redis.get_rc_latency()

    def run(self):
        latency_w1 = self.extract_latency_data("1")
        latency_w3 = self.extract_latency_data("3")
        latency_w6 = self.extract_latency_data("6")

        batch_w1, batch_w3, batch_w6 = self.latency2batch(latency_w1, latency_w3, latency_w6)
        # batch_w3 = self.latency2batch(latency_w3, 3)
        # batch_w6 = self.latency2batch(latency_w6, 6)

        self.end2end_comparison_graph([batch_w1, batch_w3, batch_w6])

    def latency2batch(self, latw1, latw3, latw6):
        tmp_totalw1, tmp_totalw3, tmp_totalw6 = 0, 0, 0
        batch_w1, batch_w3, batch_w6 = [], [], []
        for i in range(len(latw1)):
            frame_id = i + 1
            tmp_totalw1 += latw1[i]
            tmp_totalw3 += latw3[i]
            tmp_totalw6 += latw6[i]

            if frame_id % 6 == 0:
                batch_w1.append(tmp_totalw1)
                batch_w3.append((tmp_totalw3/2))
                batch_w6.append((tmp_totalw6/6))

                tmp_totalw1, tmp_totalw3, tmp_totalw6 = 0, 0, 0 #reset

        return batch_w1, batch_w3, batch_w6

    def extract_latency_data(self, worker_id):
        # yolo_read = self.read_data('06_yolo_load_img_latency-w=%s.csv' % worker_id)
        yolo_inference = self.read_data('07_yolo_inference_latency-w=%s.csv' % worker_id)
        yolo_nms = self.read_data('08_yolo_nms_latency-w=%s.csv' % worker_id)
        modv2 = self.read_data('14_yolo_modv2_latency-w=%s.csv' % worker_id)

        # print("LEN: ", len(yolo_read), len(yolo_inference), len(yolo_nms), len(modv2))

        this_latency = []
        for i in range (len(yolo_inference)):
            # total_ms = yolo_read[i] + yolo_inference[i] + yolo_nms[i] + modv2[i]
            total_ms = yolo_inference[i] + yolo_nms[i] + modv2[i]
            this_latency.append(total_ms)

        return this_latency
        # return [yolo_read, yolo_inference, yolo_nms, modv2]

    def save_to_csv(self, fname, data):
        np.savetxt(self.latency_output + fname, data, delimiter=',')  # X is an array

    def read_data(self, fname):
        fpath = self.latency_output + fname
        with open(fpath, 'r') as f:
            reader = csv.reader(f)
            return [float(line[0]) for line in list(reader)]

    def end2end_comparison_graph(self, batch_latency=None):

        print(">>> batch_latency:", batch_latency)
        print(">>> LEN batch_latency:", len(batch_latency[0]))
        worker1, worker2, worker3 = None, None, None
        if batch_latency is None:
            try:
                worker1 = self.read_data('sum-latency-w=1.csv')
                worker2 = self.read_data('sum-latency-w=3.csv')
                worker3 = self.read_data('sum-latency-w=6.csv')
            except:
                pass
        else:
            worker1 = batch_latency[0]
            worker2 = batch_latency[1]
            worker3 = batch_latency[2]

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

            # print(worker1)

            mean_worker1 = round(np.mean(np.array(worker1)), 2)
            mean_worker2 = round(np.mean(np.array(worker2)), 2)
            mean_worker3 = round(np.mean(np.array(worker3)), 2)

            min_worker1 = round(np.min(np.array(worker1)), 2)
            min_worker2 = round(np.min(np.array(worker2)), 2)
            min_worker3 = round(np.min(np.array(worker3)), 2)

            max_worker1 = round(np.max(np.array(worker1)), 2)
            max_worker2 = round(np.max(np.array(worker2)), 2)
            max_worker3 = round(np.max(np.array(worker3)), 2)

            # w1_to_w2 = round(((mean_worker1/mean_worker2)*100), 2)
            # w1_to_w3 = round(((mean_worker1/mean_worker3)*100), 2)
            # (new - old)/old*100
            w1_to_w2 = round(((mean_worker2 - mean_worker1)/mean_worker1*100), 2)
            w1_to_w3 = round(((mean_worker3 - mean_worker1)/mean_worker1*100), 2)

            print(" >> mean_worker1:", mean_worker1)
            print(" >> mean_worker2:", mean_worker2)
            print(" >> mean_worker3:", mean_worker3)

            print(" >> min_worker1:", min_worker1)
            print(" >> min_worker2:", min_worker2)
            print(" >> min_worker3:", min_worker3)

            print(" >> max_worker1:", max_worker1)
            print(" >> max_worker2:", max_worker2)
            print(" >> max_worker3:", max_worker3)

            print(" >> w1_to_w2:", w1_to_w2, " %")
            print(" >> w1_to_w3:", w1_to_w3, " %")


            fig = plt.figure()
            # title = "Comparison of Pattern Recognition Latency"
            title = "Pattern Recognition Latency of TM-04 + %s" % self.opt.mod_version
            # title = "Pattern Recognition Latency of TM-06 + %s" % self.opt.mod_version
            plt.title(title)
            plt.plot(ks, worker1, label='1 Worker')
            plt.plot(ks, worker2, label='3 Workers')
            plt.plot(ks, worker3, label='6 Workers')

            plt.axhline(mean_worker1, color='blue', linestyle='dashed', linewidth=1)
            plt.axhline(mean_worker2, color='orange', linestyle='dashed', linewidth=1)
            plt.axhline(mean_worker3, color='green', linestyle='dashed', linewidth=1)

            plt.xlabel('Frame Batch Number (6 Frames / Batch)')
            plt.ylabel('Latency (ms)')
            plt.legend()

            # x_info = [str(i) for i in range(1, K + 1)]
            # plt.xticks(ks, x_info)

            plt.show()
            print("##### Saving graph into: ", self.latency_output + 'end2end_latency_per_frame.png')
            # fig.savefig(self.latency_output + 'PR_latency_comparison_%s.png' % self.opt.mod_version, dpi=fig.dpi)
            fig.savefig(self.latency_output + 'PR_latency_comparison_%s.pdf' % self.opt.mod_version, dpi=fig.dpi)
            print("saved file into:", self.latency_output + 'PR_latency_comparison_%s.pdf')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--mod_version', type=str, default="MODv1", help="Version of MOD used in this plot")
    # parser.add_argument('--mod_version', type=str, default="MODv2", help="Version of MOD used in this plot")
    parser.add_argument('--mod_version', type=str, default="MOD", help="Version of MOD used in this plot")
    # parser.add_argument("--output_graph", type=str, default="output_graph/modv2/v2/", help="path to save the graphs")
    parser.add_argument("--output_graph", type=str, default="output_graph/modv2/v2_tm04_2/", help="path to save the graphs")
    opt = parser.parse_args()
    print(opt)

    Plot(opt).run()

