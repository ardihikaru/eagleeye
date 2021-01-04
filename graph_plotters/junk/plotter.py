"""
Source:
    https://medium.com/python-in-plain-english/make-a-beautiful-bar-chart-in-just-few-lines-in-python-5625ebc71c49

"""
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType
bar = (
    Bar()
    .add_xaxis(['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'])
    .add_yaxis("Temperature Max", [-7,-6,-2,4,10,15,18,17,13,7,2,-3],color="#1565C0")
    .add_yaxis("Temperature Min", [-1,0,5,12,18,24,27,26,21,14,8,2],color='#80CBC4')
    .set_global_opts(title_opts=opts.TitleOpts(title="30-year temperature for Toronto", subtitle="Year 1981 to 2010"))
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        markpoint_opts=opts.MarkPointOpts(
        data=[opts.MarkPointItem(type_="max", name="Highest Temp"),
              opts.MarkPointItem(type_="min", name="Lowest Temp"),]),
                )
                )
bar.render_notebook()
