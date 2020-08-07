"""
   This is a Controller class to manage any action related with /api/plot endpoint
"""

from ext_lib.utils import get_json_template
import asab
from ext_lib.redis.my_redis import MyRedis
from ews.controllers.latency.latency import Latency
from ext_lib.utils import int_to_tuple, get_current_datetime
import matplotlib.pyplot as plt
import numpy as np
import csv
from os import path
import os


class Plot(MyRedis):
    def __init__(self):
        super().__init__(asab.Config)
        self.latency = Latency()
        self.save_dir = asab.Config["plot"]["root_path"] + get_current_datetime(is_folder=True) + "/"
        self.color = ["blue", "orange", "green", "purple"]

        # Create folder if not yet exist
        if not path.exists(self.save_dir):
            os.mkdir(self.save_dir)

    def _gen_latency_graph_list(self, latency_data, summary, num_data):
        # Define number of iteration (K)
        K = num_data
        ks = int_to_tuple(K)  # used to plot the results

        # Set plot configuration
        fig = plt.figure()
        title = "Proc. Latency PiH Candidate"
        plt.title(title)

        # Plot latency data
        for section, latency in latency_data.items():
            plt.plot(ks, latency, label=section)

            # print(">> Section=%s; MIN=%s; MAX=%s; AVG=%s" % (section, str(min_val[section]), str(max_val[section]),
            #                                                  str(avg_val[section])))

        # Plot Min, Max, and Average
        # color = ["blue", "orange", "green"]
        # for i in range(len(latency_data)):
        #     plt.axhline(mean_worker1, color='blue', linestyle='dashed', linewidth=1)

        plt.xlabel('Frame ID')
        plt.ylabel('Latency (ms)')
        plt.legend()

        # Save plot result
        fig.savefig(self.save_dir + 'proc_lat_pih_candidate_.png', dpi=fig.dpi)
        fig.savefig(self.save_dir + 'proc_lat_pih_candidate_.pdf', dpi=fig.dpi)
        print("saved file into:", 'proc_lat_pih_candidate_.pdf (And .png)')

    def _gen_latency_graph(self, latency_title, latency_data, summary, num_data):
        print(" >>> latency_data:", latency_data)
        # Define number of iteration (K)
        K = num_data
        ks = int_to_tuple(K)  # used to plot the results

        # Set plot configuration
        fig = plt.figure()
        title = "Proc. Latency %s" % latency_title
        plt.title(title)

        # Plot latency data
        plt.plot(ks, latency_data, label=latency_title)

        # Plot Min, Max, and Average
        i = -1
        for sum_str, val in summary.items():
            i += 1
            plt.axhline(val, color=self.color[i], linestyle='dashed', label=sum_str+" (%s ms)" % str(val), linewidth=1)

        plt.xlabel('Frame ID')
        plt.ylabel('Latency (ms)')
        plt.legend()

        # Save plot result
        fig.savefig(self.save_dir + 'proc_lat_%s.png' % latency_title, dpi=fig.dpi)
        fig.savefig(self.save_dir + 'proc_lat_%s_.pdf' % latency_title, dpi=fig.dpi)
        print("saved file into:", 'proc_lat_%s_.pdf (And .png)' % latency_title)

    def _get_summary_latency(self, latency):
        # Set min, max, and avg params
        summary = {}

        # Summarize data
        for section, data in latency.items():
            summary[section] = {
                "min": round(np.min(np.array(data)), 2),
                "max": round(np.max(np.array(data)), 2),
                "mean": round(np.mean(np.array(data)), 2)
            }

        return summary

    # TODO: To add try-catch handler
    def plot_det_latency(self, plot_data):
        print(" >>> plot_data:", plot_data)

        # Collect latency data
        latency, num_data = {}, 0
        for section in plot_data["section"]:
            tmp_lat_data = self.latency.get_data_by_section(section)["data"]
            # Reformat latency data
            latency[section] = [data["latency"] for data in tmp_lat_data]
            num_data = len(tmp_lat_data)

        # Collect summary data: MIN, MAX, and AVERAGE
        summary = self._get_summary_latency(latency)
        print(" >>> TYPE. summary", type(summary), summary)

        # Generate graph
        try:
            i = -1
            for section, lat in latency.items():
                i += 0
                # self._gen_latency_graph(section, lat, summary[section], num_data)
                self._gen_latency_graph(plot_data["name"][i], lat, summary[section], num_data)
        except Exception as e:
            print(" >>> ERROR: ", str(e))

        latency["summary"] = summary
        return get_json_template(response=True, results=latency, total=-1, message="OK")

    # TODO: To add try-catch handler
    def plot_e2e_latency(self, plot_data):
        print(" >>> plot_data:", plot_data)

        # Collect latency data
        # latency, num_data = {}, 0
        # num_data = 0
        tmp_lat_data = self.latency.get_data_by_section(plot_data["section"])["data"]
        # Reformat latency data
        latency_e2e = [data["latency"] for data in tmp_lat_data]
        num_data = len(tmp_lat_data)

        # Collect summary data: MIN, MAX, and AVERAGE
        summary = self._get_summary_latency(latency)
        print(" >>> TYPE. summary", type(summary), summary)

        # Generate graph
        try:
            for section, lat in latency.items():
                self._gen_latency_graph(section, lat, summary[section], num_data)
        except Exception as e:
            print(" >>> ERROR: ", str(e))

        latency["summary"] = summary
        return get_json_template(response=True, results=latency, total=-1, message="OK")
