from utils.utils import *

latency_output = "saved_latency"

class Plot:
    def __init__(self):
        self.latency_output = "saved_latency"
        self.sub_path = "/tmp"
        self.csv_inference = "time_inference_latency.csv"
        self.csv_nms = "time_nms_latency.csv"
        self.csv_mbbox = "time_mbbox_latency.csv"
        self.csv_default = "time_bbox_latency.csv"

    def run(self):
        self.__overall_graph()
        self.__bbox_mbbox_graph()
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

    def __bbox_mbbox_graph(self):
        comp_path = self.latency_output + "/comparison/"
        time_bbox_latency = read_data(comp_path+"default", self.csv_default)
        time_mbbox_latency = read_data(comp_path+"custom", self.csv_mbbox)
        # time_bbox_latency = read_data(self.latency_output, self.csv_default)
        # time_mbbox_latency = read_data(self.latency_output, self.csv_mbbox)

        # Define number of iteration (K)
        K = len(time_bbox_latency)
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        title = "Processing Latency of PR Model with MOD: NMS + MB-Box"
        plt.title(title)
        plt.plot(ks, time_bbox_latency, label='Default B-Box Latency')
        plt.plot(ks, time_mbbox_latency, label='MB-Box Latency')
        plt.xlabel('Frame ID')
        plt.ylabel('Latency (ms)')
        plt.legend()
        plt.show()
        fig.savefig(self.latency_output + '/latency_bbox-mbbox.png', dpi=fig.dpi)

    def __comparison_graph(self):
        comp_path = self.latency_output + "/comparison/"
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
            custom_latency.append( c_time_inference_latency[i] + c_time_nms_latency[i] + c_time_bbox_latency[i] )
            default_latency.append( d_time_inference_latency[i] + d_time_nms_latency[i] + d_time_mbbox_latency[i] )

        # Define number of iteration (K)
        K = len(c_time_inference_latency)
        ks = int_to_tuple(K)  # used to plot the results

        fig = plt.figure()
        title = "Comparison: Processing Latency with MOD VS without MOD"
        plt.title(title)
        plt.plot(ks, custom_latency, label='Total Latency (with MOD)')
        plt.plot(ks, default_latency, label='Total Latency (Without MOD)')
        plt.xlabel('Frame ID')
        plt.ylabel('Latency (ms)')
        plt.legend()
        plt.show()
        fig.savefig(self.latency_output + '/latency_comparison.png', dpi=fig.dpi)

if __name__ == '__main__':
    Plot().run()
