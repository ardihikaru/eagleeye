from utils.utils import *
import matplotlib.patches as mpatches

latency_output = "saved_latency"

class Plot:
    def __init__(self):
        self.latency_output = "saved_latency"
        # self.sub_path = "/tmp"
        self.sub_path = "/comparison-gpu/custom"
        self.csv_inference = "time_inference_latency.csv"
        self.csv_nms = "time_nms_latency.csv"
        self.csv_mbbox = "time_mbbox_latency.csv"
        self.csv_default = "time_bbox_latency.csv"

    def run(self):
        self.__overall_graph()
        self.__mbbox_graph()
        self.__comparison_graph()

    def __overall_graph(self):
        time_inference_latency = read_data(self.latency_output+self.sub_path, self.csv_inference)
        time_nms_latency = read_data(self.latency_output+self.sub_path, self.csv_nms)
        time_mbbox_latency = read_data(self.latency_output+self.sub_path, self.csv_mbbox)

        # Define number of iteration (K)
        K = len(time_inference_latency)
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        # title = "Processing Latency of PR Model with MOD (Merge Object Detection)"
        title = "Processing Latency of PR Model with MOD"
        plt.title(title)
        plt.plot(ks, time_inference_latency, label='Inference Latency')
        plt.plot(ks, time_nms_latency, label='NMS Latency')
        plt.plot(ks, time_mbbox_latency, label='MB-Box Latency')
        plt.xlabel('Frame ID')
        plt.ylabel('Latency (ms)')
        plt.legend()
        plt.show()
        fig.savefig(self.latency_output + '/latency_overall.png', dpi=fig.dpi)

    def __mbbox_graph(self):
        comp_path = self.latency_output + "/comparison-gpu/"
        # time_bbox_latency = read_data(comp_path+"default", self.csv_default)
        time_mbbox_latency = read_data(comp_path+"custom", self.csv_mbbox)
        # time_bbox_latency = read_data(self.latency_output, self.csv_default)
        # time_mbbox_latency = read_data(self.latency_output, self.csv_mbbox)

        # optional remove bad data
        del time_mbbox_latency[0]
        del time_mbbox_latency[1]

        mean_mbbox = round(np.mean(np.array(time_mbbox_latency)) * 1000, 2)

        for i in range(len(time_mbbox_latency)):
            # time_bbox_latency[i] = time_bbox_latency[i] * 1000
            time_mbbox_latency[i] = time_mbbox_latency[i] * 1000

        # Define number of iteration (K)
        K = len(time_mbbox_latency)
        ks = int_to_tuple(K)  # used to plot the results

        # red_patch = mpatches.Patch(color='red', label='The red data')
        # blue_patch = mpatches.Patch(color='blue', label='The blue data')

        fig = plt.figure()
        title = "Processing Latency of MOD Algorithm (GPU)"
        plt.title(title)
        plt.plot(ks, time_mbbox_latency, label='MB-Box Latency')
        # plt.plot(ks, time_bbox_latency, label='Default B-Box Latency')
        plt.axhline(np.mean(np.array(mean_mbbox)), color='red', linestyle='dashed', linewidth=2, label='Average Latency')
        plt.xlabel('Frame ID for NCTU Custom Dataset (5 seconds)')
        plt.ylabel('Latency (ms)')
        plt.legend()
        # plt.legend(handles=[red_patch, blue_patch])
        plt.show()
        fig.savefig(self.latency_output + '/latency_bbox-mbbox.png', dpi=fig.dpi)

    def __comparison_graph(self):
        comp_path = self.latency_output + "/comparison-gpu/"
        c_time_inference_latency = read_data(comp_path+"custom", self.csv_inference)
        c_time_nms_latency = read_data(comp_path+"custom", self.csv_nms)
        c_time_bbox_latency = read_data(comp_path+"custom", self.csv_default)

        d_time_inference_latency = read_data(comp_path+"default", self.csv_inference)
        d_time_nms_latency = read_data(comp_path+"default", self.csv_nms)
        d_time_mbbox_latency = read_data(comp_path+"default", self.csv_mbbox)

        # get total latency
        custom_latency = []
        default_latency = []
        for i in range(len(c_time_inference_latency)):
            if i < 2:
                continue
            cust_lat = c_time_inference_latency[i] + c_time_nms_latency[i] + c_time_bbox_latency[i]
            def_lat = d_time_inference_latency[i] + d_time_nms_latency[i] + d_time_mbbox_latency[i]

            cust_lat = cust_lat * 1000
            def_lat = def_lat * 1000

            custom_latency.append(cust_lat)
            default_latency.append(def_lat)

        # Define number of iteration (K)
        # K = len(c_time_inference_latency)
        K = len(c_time_inference_latency) - 2
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        # title = "Comparison: Processing Latency with MOD VS without MOD"
        title = "Processing Latency of PR Model (GPU)"
        plt.title(title)
        plt.plot(ks, custom_latency, label='Total Latency (with MOD)')
        plt.plot(ks, default_latency, label='Total Latency (Without MOD)')
        plt.xlabel('Frame ID for NCTU Custom Dataset (5 seconds)')
        plt.ylabel('Latency (ms)')
        plt.legend()
        plt.show()
        fig.savefig(self.latency_output + '/latency_comparison.png', dpi=fig.dpi)

if __name__ == '__main__':
    Plot().run()
