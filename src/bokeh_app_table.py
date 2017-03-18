
from random import random

from bokeh.layouts import column
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc

from socketIO_client import SocketIO
import uuid


# create a plot and style its properties
p = figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
p.border_fill_color = 'black'
p.background_fill_color = 'black'
p.outline_line_color = None
p.grid.grid_line_color = None

# add a text renderer to out plot (no data yet)
r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="20pt",
           text_baseline="middle", text_align="center")

i = 0

ds = r.data_source

def on_response(msg, *args):
    global ds
    new_data = dict()
    new_data['x'] = ds.data['x'] + [random() * 70 + 15]
    new_data['y'] = ds.data['y'] + [random() * 70 + 15]
    new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i % 3]]
    new_data['text'] = msg
    ds.data = new_data
    print(msg)

baseurl = "http://emsapi.eu-west-2.elasticbeanstalk.com"
socketIO = SocketIO(baseurl)
# socketIO.on('onMarketData', print)
# print('Subscribing...')
# socketIO.emit('subscribe',
#               ['AAPL', 'AMD', 'BAC', 'BMY', 'C', 'CSCO', 'CYH', 'FB', 'FCX', 'GE', 'INTC', 'MDLZ', 'MSFT', 'WMT', 'MU',
#                'INTC', 'PFE', 'VZ', 'WFZ', 'WMT', 'XOM'])
socketIO.on('onOrderMessage', on_response)

# create a callback that will add a number in a random location
def callback():
    global i, socketIO
    newOrder = {'type': 'NewOrder',
                'clientOrderId': str(uuid.uuid4()),
                'symbol': 'AAPL',
                'buySell': 'SELL',
                'qty': '100'}
    socketIO.emit('submitOrder', newOrder)
    socketIO.wait(seconds=0.5)
    print(newOrder)
    i = i + 1

# add a button widget and configure with the call back
button = Button(label="Press Me")
button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(button, p))