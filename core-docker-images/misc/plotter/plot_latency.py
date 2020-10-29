import matplotlib.pyplot as plt
import numpy as np
from os import path
import os
import csv
from datetime import datetime, timedelta


def int_to_tuple(Ks):
    lst = []
    for i in range(Ks):
        lst.append((i+1))
    return tuple(lst)


def read_csv(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        return [float(line[0]) for line in list(reader)]


def get_current_datetime(is_folder=False):
    if is_folder:
        return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    else:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


save_graph_dir = "./../../output/graph/" + get_current_datetime(is_folder=True) + "/"
save_csv_dir = "./../../output/csv/" + get_current_datetime(is_folder=True) + "/"
color = ["blue", "orange", "green", "purple"]


def gen_latency_graph_list(latency_title, latency_data, avg_data, num_data, xlabel, ylabel="Latency (ms)"):
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
        plt.axhline(avg_data[i], color=color[i], linestyle='dashed', linewidth=1,
                    label="AVG(%s %s) (%.2f ms)" % (num_nodes[i], node_str, avg_data[i]))

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()

    # Save plot result
    fig.savefig(save_graph_dir + 'proc_lat_%s.png' % latency_title, dpi=fig.dpi)
    fig.savefig(save_graph_dir + 'proc_lat_%s.pdf' % latency_title, dpi=fig.dpi)
    print("saved file into:", 'proc_lat_%s.pdf (And .png)' % latency_title)


def list2batchlist(list_data, batch_size, num_node):
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


def plot_node_latency(config):
    # Create folder if not yet exist
    if not path.exists(save_graph_dir):
        os.mkdir(save_graph_dir)
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
            batch = list2batchlist(lat, config["batch_size"], node["num_node"])
            avg_data.append(np.mean(batch))
            batch_data[str(node["num_node"])] = batch

        max_plot_data = int(config["max_data"] / 6)
        xlabel = "Batch"
        ylabel = "Latency (ms)"
        gen_latency_graph_list("Node comparison", batch_data, avg_data, max_plot_data, xlabel, ylabel)

    except Exception as e:
        print(e)
        os.rmdir(save_graph_dir)


json_data = {
    "node_info": [
        {
            "det_path": "/home/ardi516/devel/nctu/eagleeye/output/experimental_results/GPU_2020-08-19/w=1/csv/2020-08-19_21:57:00/e2e_latency_worker=1_n=595.csv",
            "sch_path": "/home/ardi516/devel/nctu/eagleeye/output/experimental_results/GPU_2020-08-19/w=1/csv/2020-08-19_21:57:00/scheduling_worker=1_n=596.csv",
            "num_node": 1
        },
        {
            "det_path": "/home/ardi516/devel/nctu/eagleeye/output/experimental_results/GPU_2020-08-19/w=3/csv/2020-08-19_22:09:19/e2e_latency_worker=3_n=595.csv",
            "sch_path": "/home/ardi516/devel/nctu/eagleeye/output/experimental_results/GPU_2020-08-19/w=3/csv/2020-08-19_22:09:19/scheduling_worker=3_n=596.csv",
            "num_node": 3
        },
        {
            "det_path": "/home/ardi516/devel/nctu/eagleeye/output/experimental_results/GPU_2020-08-19/w=6/csv/2020-08-19_22:19:13/e2e_latency_worker=6_n=595.csv",
            "sch_path": "/home/ardi516/devel/nctu/eagleeye/output/experimental_results/GPU_2020-08-19/w=6/csv/2020-08-19_22:19:13/scheduling_worker=6_n=596.csv",
            "num_node": 6
        }
    ],
    "batch_size": 6,
    "max_data": 120,
    "include_scheduling": True
}

plot_node_latency(json_data)
