# from flask import Flask, render_template
# from flask_socketio import SocketIO, send, emit
# 
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)
# 
# 
# @socketio.on('message')
# def handle_message(message):
#   print('received message: ' + message)
#   send('Echoing: ' + message)
# 
# 
# if __name__ == '__main__':
#   socketio.run(app)
from socketIO_client import SocketIO
import couchdb
import json
import ipdb

couchdb_server = couchdb.client.Server('http://localhost:5984/')
db = couchdb_server['hackathon']

def on_response(msg, *args):
  print('on_message', msg)
  db.save(msg)

baseurl = "http://emsapi.eu-west-2.elasticbeanstalk.com"
with SocketIO(baseurl) as socketIO:
  socketIO.on('onMarketData', on_response)
  print('Subscribing...')
  socketIO.emit('subscribe', ['AAPL','AMD','BAC', 'BMY', 'C', 'CSCO', 'CYH', 'FB', 'FCX', 'GE', 'INTC', 'MDLZ', 'MSFT', 'WMT', 'MU', 'INTC', 'PFE', 'VZ', 'WFX', 'WMT', 'XOM'])
  socketIO.wait()
