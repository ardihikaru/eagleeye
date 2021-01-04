import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

raw_data = {'plan_type': ['A1', 'A2', 'A3'],
	        'original': [925, 312, 72],
	        'cur_work': [570, 124, 61]

    }
# df2 =pd.DataFrame(raw_data, columns = ['plan_type', 'Group A'])
df = pd.DataFrame(raw_data,
                  # columns = ['plan_type', 'Group B', 'Group C', 'Group D', 'Group E'])
                  columns = ['plan_type', 'original', 'cur_work'])

# ax = df2.plot.bar(rot=0,color='#FFFFFF',width=1)
# ax = df.plot.bar(rot=0, ax=ax, color=["#900C3F", '#C70039', '#FF5733', '#FFC300'],
ax = df.plot.bar(rot=0, color=["#C70039", '#38761D'],
                 width = 0.8 )

for p in ax.patches[0:]:
    h = p.get_height()
    x = p.get_x()+p.get_width()/2.
    if h != 0:
        ax.annotate("%g" % p.get_height(), xy=(x,h), xytext=(0,4), rotation=90,
                   textcoords="offset points", ha="center", va="bottom")

ax.set_xlim(-0.7, None)
ax.margins(y=0.2)
# ax.legend(ncol=len(df.columns), loc="lower left", bbox_to_anchor=(0,1.02,1,0.08),
#           borderaxespad=0, mode="expand")
ax.set_xticklabels(df["plan_type"])
plt.grid()
plt.show()
