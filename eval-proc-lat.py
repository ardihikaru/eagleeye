from utils.utils import *
import argparse


class Plot:
    def __init__(self, opt):
        self.opt = opt
        self.latency_output = opt.csv_data

    def run(self):
        data = self.extract_latency_data()
        data_others = self.extract_latency_data("others-832.csv")
        data_preproc = self.extract_latency_data("preprocessing-832.csv")

        data.pop(0)
        data_others.pop(0)
        data_preproc.pop(0)

        mean_data = round(np.mean(np.array(data)), 3)
        mean_data_others = round(np.mean(np.array(data_others)), 3)
        mean_data_preproc = round(np.mean(np.array(data_preproc)), 3)

        print("--- mean_data:", mean_data)
        print("--- mean_data_others:", mean_data_others)
        print("--- mean_data_preproc:", mean_data_preproc)

        self.plot_graph(data)

    def extract_latency_data(self, path=None):
        if path is None:
            lat_data = self.read_data('object-detection-1000.csv')
        else:
            lat_data = self.read_data(path)

        this_latency = []
        for i in range (len(lat_data)):
            total_ms_lat = lat_data[i]
            this_latency.append(total_ms_lat)

        return this_latency

    def read_data(self, fname):
        fpath = self.latency_output + fname
        with open(fpath, 'r') as f:
            reader = csv.reader(f)
            return [float(line[0]) for line in list(reader)]

    def plot_graph(self, data=None):

        num_data = len(data)

        min_data = round(np.min(np.array(data)), 3)
        max_data = round(np.max(np.array(data)), 3)
        avg_data = round(np.mean(np.array(data)), 3)

        print("[Total data=%s] AVG=%s; MIN=%s; MAX=%s" %
              (str(num_data), str(avg_data), str(min_data), str(max_data)))

        # Define number of iteration (K)
        K = num_data
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        title = "Processing Latency"
        plt.title(title)
        plt.plot(ks, data, label='Proc. Latency')

        plt.axhline(avg_data, label='AVG (%s ms)' % str(avg_data), color='blue', linestyle='dashed', linewidth=1)
        plt.axhline(min_data, label='MIN (%s ms)' % str(min_data), color='orange', linestyle='dashed', linewidth=1)
        plt.axhline(max_data, label='MAX (%s ms)' % str(max_data), color='green', linestyle='dashed', linewidth=1)

        plt.xlabel('Frame ID')
        plt.ylabel('Latency (ms)')
        plt.legend()

        plt.show()
        fig.savefig(self.opt.output_graph + 'proc_latency_%s.png' % self.opt.img_size, dpi=fig.dpi)
        fig.savefig(self.opt.output_graph + 'proc_latency_%s.pdf' % self.opt.img_size, dpi=fig.dpi)
        print("saved file into:", self.opt.output_graph + 'proc_latency_%s.pdf (And .png)' % self.opt.img_size)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("--img_size", type=str, default="224", help="Inference size")
    # parser.add_argument("--img_size", type=str, default="416", help="Inference size")
    # parser.add_argument("--img_size", type=str, default="608", help="Inference size")
    parser.add_argument("--img_size", type=str, default="832", help="Inference size")
    parser.add_argument("--csv_data", type=str, default="exported_data/csv/proc_lat/", help="path to save the graphs")
    parser.add_argument("--output_graph", type=str, default="output_graph/proc_lat/", help="path to save the graphs")
    opt = parser.parse_args()
    print(opt)

    Plot(opt).run()

