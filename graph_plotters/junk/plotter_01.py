"""
   This is a Controller class to manage any action related with /api/plot endpoint
"""

from ext_lib.utils import get_json_template
import asab
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import int_to_tuple, get_current_datetime
import matplotlib.pyplot as plt
import numpy as np
from os import path
import os
from ext_lib.utils import save_to_csv, read_csv
import seaborn as sns


class Plot(object):
	def __init__(self):
		self.save_graph_dir = "./outputs/"
		# self.save_graph_dir = asab.Config["export"]["graph_path"] + get_current_datetime(is_folder=True) + "/"
		# self.save_csv_dir = asab.Config["export"]["csv_path"] + get_current_datetime(is_folder=True) + "/"
		self.color = ["blue", "orange", "green", "purple"]

	def _add_grid(self):
		# Show the major grid lines with dark grey lines
		plt.grid(b=True, which='major', color='#666666', linestyle='-')
		# Show the minor grid lines with very faint and almost transparent grey lines
		plt.minorticks_on()
		plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

	def _add_latex_config(self, latex_ready):
		"""

		If error:
			`RuntimeError: Failed to process string with tex because latex could not be found`

		Source:
			https://blog.csdn.net/weixin_42419002/article/details/103997521

		Solution:
			$ pip install latex
			$ sudo apt-get install dvipng
			$ sudo apt-get install -y texlive texlive-latex-extra texlive-latex-recommended
			$ sudo apt-get install cm-super
				>> https://stackoverflow.com/questions/31214214/matplotlib-error-latex-was-not-able-to-process-the-following-string-lp

		"""
		if latex_ready:
			# Set default configuration for the plot
			font = {'weight': 'bold',
			        'size': 23}
			plt.rc('font', **font)
			# plt.subplots_adjust(bottom=.07, top=.9, left=.05, right=.95)
			plt.subplots_adjust(bottom=.10, top=.9, left=.09, right=.95)
			plt.rc('text', usetex=True)
			sns.set(style="white")

	def plot_data(self, latency_title, latency_data, avg_data, num_data, xlabel, ylabel="Latency (ms)",
	              data_label="node", latex_ready=False):
		# Define number of iteration (K)
		ks = int_to_tuple(int(num_data))  # used to plot the results

		# Set plot configuration
		fig = plt.figure()
		self._add_grid()
		plt.title(latency_title)

		# Verify the config.
		# Please install latex in your Local first --> In Linux: $ sudo apt install texlive-full
		# otherwise you will get an error, such as `Failed to process string with tex because latex could not be found`
		self._add_latex_config(latex_ready)

		# Plot latency data
		# num_nodes = []
		# for num_node, latency in latency_data.items():
		# 	node_str = data_label if int(num_node) == 1 else (data_label + "s")
		# 	print(">>>> latency:", latency)
		# 	plt.plot(ks, latency, label="%s %s" % (num_node, node_str))
		# 	num_nodes.append(num_node)

		# plt.bar(ks, latency, label="%s %s" % (num_node, node_str))
		barlist = plt.bar(ks, latency_data)
		barlist[0].set_color('r')

		# Plot Min, Max, and Average
		# for i in range(len(avg_data)):
		# 	node_str = data_label if int(num_nodes[i]) == 1 else (data_label + "s")
		# 	plt.axhline(avg_data[i], color=self.color[i], linestyle='dashed', linewidth=1,
		# 	            label="AVG(%s %s) (%.2f ms)" % (num_nodes[i], node_str, avg_data[i]))
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		plt.legend()

		# Save plot result
		fig.savefig(self.save_graph_dir + 'proc_lat_%s.png' % latency_title, dpi=fig.dpi)
		fig.savefig(self.save_graph_dir + 'proc_lat_%s.pdf' % latency_title, dpi=fig.dpi)
		print("saved file into:", 'proc_lat_%s.pdf (And .png)' % latency_title)


# latency_data = {
# 	1: [1],
# 	2: [4],
# 	3: [7]
# }
latency_data = [1, 4, 5]

plotter = Plot()
plotter.plot_data(
	latency_title="title",
	latency_data=latency_data,
	avg_data=[],
	num_data=3,
	xlabel="xlabel",
	ylabel="Latency (ms)",
	data_label="node",
	latex_ready=False
	# latex_ready=True
)
