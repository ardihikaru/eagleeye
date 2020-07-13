from utils.utils import *
import argparse


class Plot:
    def __init__(self, opt):
        self.opt = opt
        self.latency_output = opt.csv_data

    def run(self):
        data = self.extract_latency_data()
        # pop first 30 data ..
        for i in range(31):
            data.pop(i)

        fps_data = []
        t_stamp = 0
        total_frames = 0
        total_frames_this = 0
        sec = 1
        for ts_data in data:
            total_frames += 1
            total_frames_this += 1
            t_stamp += ts_data
            # print(" ---- Reading %s frames in (%.5fs)" % (total_frames, t_stamp))

            if t_stamp > sec:
                print(" ---- SEC=%s --> Reading %s frames; Current Elapsed time (%.5fs)" %
                      (str(sec), str(total_frames_this), t_stamp))
                fps_data.append(total_frames_this)
                sec += 1
                total_frames_this = 0

        # self.plot_graph(data)
        fps_data.pop(32)
        fps_data.pop(31)
        fps_data.pop(30)
        fps_data.pop(29)
        fps_data.pop(28)
        fps_data.pop(27)
        fps_data.pop(26)
        fps_data.pop(0)
        # fps_data.pop(24)
        # fps_data.pop(25)
        # fps_data.pop(26)
        # fps_data.pop(27)
        # fps_data.pop(28)

        # fps_data.pop(29)
        # fps_data.pop(30)
        self.plot_graph(fps_data)

    def extract_latency_data(self):
        lat_data = self.read_data('data.csv')

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
        title = "Frame rate per second"
        plt.title(title)
        plt.plot(ks, data, label='Time to process a frame')

        plt.axhline(avg_data, label='AVG (%s ms)' % str(avg_data), color='blue', linestyle='dashed', linewidth=1)
        plt.axhline(min_data, label='MIN (%s ms)' % str(min_data), color='orange', linestyle='dashed', linewidth=1)
        plt.axhline(max_data, label='MAX (%s ms)' % str(max_data), color='green', linestyle='dashed', linewidth=1)

        plt.xlabel('Frame ID')
        plt.ylabel('Time to read a frame (ms)')
        plt.legend()

        plt.show()
        fig.savefig(self.opt.output_graph + 'collected_frames.png', dpi=fig.dpi)
        fig.savefig(self.opt.output_graph + 'collected_frames.pdf', dpi=fig.dpi)
        print("saved file into:", self.opt.output_graph + 'collected_frames.pdf (And .png)')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_data", type=str, default="exported_data/csv/collected_frames/", help="path to save the graphs")
    parser.add_argument("--output_graph", type=str, default="output_graph/collected_frames/", help="path to save the graphs")
    opt = parser.parse_args()
    print(opt)

    Plot(opt).run()

