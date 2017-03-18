# bokeh_app

# Threading stuff
from functools import partial
from threading import Thread
from tornado import gen

from time import time
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Button
from bokeh.plotting import figure, curdoc
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, Panel, Tabs

from collections import defaultdict
import numpy as np
from socketIO_client import SocketIO
import pandas as pd
import uuid


data = defaultdict(list)

dummy = {'time': 1489848786328, 'type': 'BBO', 'symbol': 'AAPL', 'bid': '136.3300', 'ask': '136.3700'}

ds = ColumnDataSource({k: [v] for (k, v) in dummy.items()})
# Data table
columns = [TableColumn(field=k, title=k) for k in dummy.keys()]
data_table = DataTable(source=ds, columns=columns, width=600, height=300)
# tab1 = Panel(child=data_table, title='Table')

doc = curdoc()

def on_response(msg):
    doc.add_next_tick_callback(partial(update, msg))

@gen.coroutine
def update(msg):
    if msg['type']=='BBO':
        # [data[k].append(v) for (k, v) in msg.items()]
        # [data[k].append(v) for (k, v) in msg.items()]
        print(msg)
        ds.stream({k: [v] for (k, v) in msg.items()})

# Fetch some data
baseurl = "http://emsapi.eu-west-2.elasticbeanstalk.com"
socketIO = SocketIO(baseurl)
socketIO.on('onMarketData', on_response)
print('Subscribing...')
socketIO.emit('subscribe', ['AAPL'])


def blocking_ws():
    print('SOCKET STARTED')
    print(socketIO)
    socketIO.wait()
    print('============================loooop')


# Stock plots
p1 = figure(x_axis_type="datetime", title="AAPL")
p1.grid.grid_line_alpha=0.3
p1.xaxis.axis_label = 'Date'
p1.yaxis.axis_label = 'Price'
p1.line(ds['time'], ds['bid'], legend='bid')
p1.line(ds['time'], ds['ask'], legend='ask')
# #
# p1.line(datetime(AAPL['date']), AAPL['adj_close'], color='#A6CEE3', legend='AAPL')
# p1.line(datetime(GOOG['date']), GOOG['adj_close'], color='#B2DF8A', legend='GOOG')
# p1.line(datetime(IBM['date']), IBM['adj_close'], color='#33A02C', legend='IBM')
# p1.line(datetime(MSFT['date']), MSFT['adj_close'], color='#FB9A99', legend='MSFT')
p1.legend.location = "top_left"

# Make tabs


# put the button and plot in a layout and add to the document
doc.add_root(column(data_table, p1))


ws_thread = Thread(target=blocking_ws)
ws_thread.start()
