# How we can generate grouped BAR plot in Python
# loading libraries
import pandas as pd
import matplotlib.pyplot as plt


def plot_bar():
	print('**How we can generate grouped BAR plot in Python**\n')

	# Creating dataframe
	exam_data = {'name': ['1', '3', '6'],
	             'original': [925, 312, 72],
	             'cur_work': [570, 124, 61]
	             }
	df = pd.DataFrame(exam_data, columns=['name', 'original', 'cur_work'])
	print()
	print(df)

	# Setting the positions and width for the bars
	pos = list(range(len(df['original'])))
	width = 0.25

	# Plotting the bars
	fig, ax = plt.subplots(figsize=(11, 7))

	# Creating a bar with Maths_score data
	plt.bar(pos, df['original'], width, alpha=0.8, color='#1C4587')
	# plt.show()

	# Creating a bar with Science_score data,
	plt.bar([p + width for p in pos], df['cur_work'], width, alpha=0.8, color='#38761D')
	# plt.show()

	# Setting the x axis label
	ax.set_xlabel('Number of worker node')

	# Setting the y axis label
	ax.set_ylabel('Latency (ms)')

	# Setting the chart's title
	ax.set_title('')

	# Setting the position of the x ticks
	ax.set_xticks([p + 1.5 * width for p in pos])

	# Setting the labels for the x ticks
	ax.set_xticklabels(df['name'])

	# Setting the x-axis and y-axis limits
	plt.xlim(min(pos) - width, max(pos) + width * 2)
	plt.ylim([0, max(df['original'] + df['cur_work'])])

	# add values in each bar
	for p in ax.patches[1:]:
		h = p.get_height()
		x = p.get_x() + p.get_width() / 2.
		if h != 0:
			ax.annotate("%g" % p.get_height(), xy=(x, h), xytext=(0, 4), rotation=90,
			            textcoords="offset points", ha="center", va="bottom")

	# Adding the legend and showing the plot
	plt.legend(['Original', 'Current Implementation'], loc='upper left')
	plt.grid()
	plt.show()


plot_bar()
