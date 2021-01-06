"""
	>> FOR LATEX version <<
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

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc, rcParams
import seaborn as sns


# save dir
save_graph_dir = "./outputs/"

# Set plot configuration
fig = plt.figure()

# title
graph_title = "bar_graph"

# activate latex text rendering
# $ sudo apt-get install cm-super
font = {'weight': 'bold',
        'size': 12}
rc('font', **font)
rc('text', usetex=True)
rc('axes', linewidth=3)
# rc('font', weight='bold')
rcParams['text.latex.preamble'] = [r'\usepackage{sfmath} \boldmath']
# plt.subplots_adjust(bottom=.10, top=.9, left=.09, right=.95)
rc('text', usetex=True)
sns.set(style="white")

raw_data = {'num_nodes': ['1', '3', '6'],
	        'original': [925, 312, 72],
	        'cur_work': [570, 124, 61]

    }
df = pd.DataFrame(raw_data,
                  columns=['num_nodes', 'original', 'cur_work'])

# ax = df2.plot.bar(rot=0,color='#FFFFFF',width=1)
# ax = df.plot.bar(rot=0, ax=ax, color=["#900C3F", '#C70039', '#FF5733', '#FFC300'],
ax = df.plot.bar(rot=0, color=["#C70039", '#38761D'],
                 width=0.8)

for p in ax.patches[0:]:
	h = p.get_height() + 10
	x = p.get_x()+p.get_width()/2.
	if h != 0:
		ax.annotate("%g" % p.get_height(), xy=(x, h), xytext=(0, 2), rotation=0,
                   textcoords="offset points", ha="center", va="bottom")

# Setting the x axis label
# ax.set_xlabel('Number of worker node', fontsize=12.0, fontweight='bold')
ax.set_xlabel('Number of worker node')

# Setting the y axis label
# ax.set_ylabel('Latency (ms)', fontsize=12.0, fontweight='bold')
ax.set_ylabel('Latency (ms)')

ax.set_xlim(-0.7, None)
ax.margins(y=0.2)
ax.set_xticklabels(df["num_nodes"])

legend_properties = {'weight': 'bold'}
plt.legend(['Original', 'Current Implementation'], loc='upper right', prop=legend_properties)

# Setup grid
# Show the major grid lines with dark grey lines
plt.grid(b=True, which='major', color='#666666', linestyle='-')
# Show the minor grid lines with very faint and almost transparent grey lines
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

# plt.show()

plt.savefig(save_graph_dir + 'proc_lat_%s.png' % graph_title, dpi=fig.dpi)
plt.savefig(save_graph_dir + 'proc_lat_%s.pdf' % graph_title, dpi=fig.dpi)
