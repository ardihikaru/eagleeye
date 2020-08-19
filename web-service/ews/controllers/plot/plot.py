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
from os import path
import os
from ext_lib.utils import save_to_csv, read_csv


class Plot(MyRedis):
    def __init__(self):
        super().__init__(asab.Config)
        self.latency = Latency()
        self.save_graph_dir = asab.Config["export"]["graph_path"] + get_current_datetime(is_folder=True) + "/"
        self.save_csv_dir = asab.Config["export"]["csv_path"] + get_current_datetime(is_folder=True) + "/"
        self.color = ["blue", "orange", "green", "purple"]

    def _gen_latency_graph_list(self, latency_title, latency_data, avg_data, num_data, xlabel, ylabel="Latency (ms)"):
        # Define number of iteration (K)
        ks = int_to_tuple(int(num_data))  # used to plot the results

        # Set plot configuration
        fig = plt.figure()
        plt.title(latency_title)

        # Plot latency data
        num_nodes = []
        for num_node, latency in latency_data.items():
            node_str = "node" if int(num_node) == 1 else "nodes"
            plt.plot(ks, latency, label="%s %s" % (num_node, node_str))
            num_nodes.append(num_node)

        # Plot Min, Max, and Average
        for i in range(len(avg_data)):
            node_str = "node" if int(num_nodes[i]) == 1 else "nodes"
            plt.axhline(avg_data[i], color=self.color[i], linestyle='dashed', linewidth=1,
                        label="AVG(%s %s) (%.2f ms)" % (num_nodes[i], node_str, avg_data[i]))

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()

        # Save plot result
        fig.savefig(self.save_graph_dir + 'proc_lat_%s.png' % latency_title, dpi=fig.dpi)
        fig.savefig(self.save_graph_dir + 'proc_lat_%s.pdf' % latency_title, dpi=fig.dpi)
        print("saved file into:", 'proc_lat_%s.pdf (And .png)' % latency_title)

    def _gen_latency_graph(self, latency_title, latency_data, summary,
                           num_data, xlabel="Frame ID", ylabel="Latency (ms)"):
        # print(" >>> latency_data:", latency_data)
        # Define number of iteration (K)
        ks = int_to_tuple(num_data)  # used to plot the results

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

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()

        # Save plot result
        fig.savefig(self.save_graph_dir + 'proc_lat_%s.png' % latency_title, dpi=fig.dpi)
        fig.savefig(self.save_graph_dir + 'proc_lat_%s.pdf' % latency_title, dpi=fig.dpi)
        print("saved file into:", 'proc_lat_%s.pdf (And .png)' % latency_title)

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
        # Create folder if not yet exist
        if not path.exists(self.save_graph_dir):
            os.mkdir(self.save_graph_dir)

        print(" -- plot_data:", plot_data)
        # Collect latency data
        latency, num_data = {}, 0
        for section in plot_data["section"]:
            tmp_lat_data = self.latency.get_data_by_section(section)["data"]
            # Reformat latency data
            latency[section] = [data["latency"] for data in tmp_lat_data]
            num_data = len(tmp_lat_data)

            print(" --- tmp_lat_data:", tmp_lat_data)
            print(" --- num_data:", num_data)

        # Collect summary data: MIN, MAX, and AVERAGE
        summary = self._get_summary_latency(latency)

        # Generate graph
        try:
            i = -1
            for section, lat in latency.items():
                i += 1
                self._gen_latency_graph(plot_data["name"][i], lat, summary[section], num_data)
        except Exception as e:
            print(" >>> ERROR: ", str(e))

        latency["summary"] = summary
        return get_json_template(response=True, results=latency, total=-1, message="OK")

    def export_det_latency(self, latency_data):
        # Create folder if not yet exist
        if not path.exists(self.save_csv_dir):
            os.mkdir(self.save_csv_dir)

        for section in latency_data["section"]:
            data = self.latency.get_data_by_section(section)["data"]
            latency = []
            for lat in data:
                latency.append(lat["latency"])
            csv_path = self.save_csv_dir + '%s_%s_n=%s.csv' % (section, latency_data["name"], str(len(latency)))
            save_to_csv(csv_path, latency)

        return get_json_template(response=True, results={}, total=-1, message="OK")

    def _list2batchlist(self, list_data, batch_size, num_node):
        np_data = np.asarray(list_data)

        if num_node == 6:
            batch = np.mean(np_data.reshape(-1, num_node), axis=1)
        elif num_node == 3:
            batch = np.mean(np_data.reshape(-1, num_node), axis=1)
            batch = np.sum(batch.reshape(-1, 2), axis=1)
        elif num_node == 1:
            batch = np.sum(np_data.reshape(-1, batch_size), axis=1)
        else:
            batch = np_data

        return batch

    def plot_node_latency(self, config):
        # Create folder if not yet exist
        if not path.exists(self.save_graph_dir):
            os.mkdir(self.save_graph_dir)
        try:
            latency_data = []
            avg_data = []
            batch_data = {}
            for node in config["node_info"]:
                # load csv file into a local variable
                lat_det = read_csv(node["det_path"])
                lat_det = lat_det[:config["max_data"]]
                lat_sch = read_csv(node["sch_path"])
                lat_sch = lat_sch[:config["max_data"]]

                # Check, if it will include the Scheduling latency or not?
                is_add_sch = False if "include_scheduling" not in config else config["include_scheduling"]
                lat = []
                if is_add_sch:
                    for i in range(config["max_data"]):
                        lat.append((lat_det[i] + lat_sch[i]))
                else:
                    lat = lat_det
                latency_data.append(lat)

                # convert into batch_list
                batch = self._list2batchlist(lat, config["batch_size"], node["num_node"])
                avg_data.append(np.mean(batch))
                batch_data[str(node["num_node"])] = batch

            max_plot_data = int(config["max_data"] / 6)
            xlabel = "Batch"
            ylabel = "Latency (ms)"
            self._gen_latency_graph_list("Node comparison", batch_data, avg_data, max_plot_data, xlabel, ylabel)

        except Exception as e:
            return get_json_template(response=False, results={}, total=-1, message=str(e))

        return get_json_template(response=True, results={}, total=-1, message="OK")
