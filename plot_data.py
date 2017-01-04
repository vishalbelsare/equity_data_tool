## Copyright Enzo Busseti 2016

# Insert these lines in the html file to render the plots
# <link rel="stylesheet" href="https://cdn.pydata.org/bokeh/release/bokeh-0.12.3.min.css" type="text/css" />
# <script type="text/javascript" src="https://cdn.pydata.org/bokeh/release/bokeh-0.12.3.min.js"></script>

from bokeh.plotting import figure, output_file, show
from bokeh.models import WheelZoomTool, PanTool, ResetTool, HoverTool, BoxZoomTool, Title, UndoTool
from bokeh.models.sources import ColumnDataSource
from bokeh.embed import components
import pandas as pd

#
## Value in time plot
#

returns=pd.read_csv('returns.txt',index_col=0)
returns.index = pd.to_datetime(returns.index)
cumreturns=1E4*(1+returns).cumprod()
cumreturns['oneovern']= cumreturns.mean(1)
cumreturns['Date']=cumreturns.index

p = figure(width=800, height=500, x_axis_type="datetime",
            tools=[PanTool(), WheelZoomTool(), BoxZoomTool(), UndoTool(), ResetTool()])#, webgl=True)

p.line(cumreturns['Date'], cumreturns['SPY'], color='navy', legend='SPY')
p.line(cumreturns['Date'], cumreturns['USDOLLAR'], color='red', legend='USDOLLAR')
p.line(cumreturns['Date'], cumreturns['oneovern'], color='black', legend='1/n portfolio')
p.legend.location = "bottom_left"
p.toolbar.logo=None
p.title.text = "Value of sample portfolios in time"
p.title.align = "center"
p.title.text_font_size = "25px"
p.add_layout(Title(text="Value ($)", align="center"), "left")

with open("value_time.xml",'w') as f:
    script, div = components(p)
    f.writelines(script)
    f.writelines(div)

#
## Volatility and mean return plot
#

import math
assets=pd.read_csv('assets.txt',index_col=0)
assets['std']=returns.std()*math.sqrt(250)
assets['avg']=returns.mean()*250
assets['stdstr']=assets['std'].map(lambda e: "%.2f%%"%(100*e))
assets['avgstr']=assets['avg'].map(lambda e: "%.2f%%"%(100*e))

hover = HoverTool(
        tooltips=[
            ("Symbol", "@Symbol"),
            ("Mean annualized return","@avgstr"),
            ("Mean annualized volatility","@stdstr"),
            ("Description", "@Description"),
        ]
    )

p = figure(plot_width=800, plot_height=600, title=None,
           tools=[PanTool(), WheelZoomTool(), BoxZoomTool(), UndoTool(), ResetTool(), hover])#,webgl=True)
p.circle(x='std', y='avg', source=ColumnDataSource(assets.ix[:-1]),size=10,color='blue')
p.circle(x='std', y='avg', source=ColumnDataSource(assets.ix[-1:]),size=10,color='red')

p.title.text = "Mean return vs. volatility (hover on dots)"
p.title.align = "center"
p.title.text_font_size = "25px"
p.add_layout(Title(text="Mean annualized volatility", align="center"), "below")
p.add_layout(Title(text="Mean annualized return", align="center"), "left")
p.toolbar.logo = None

with open("std_mean.xml",'w') as f:
    script, div = components(p)
    f.writelines(script)
    f.writelines(div)
