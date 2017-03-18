import ipdb
import json
import couchdb
import time
import numpy as np
import pickle
import os
from sklearn.externals import joblib
from sklearn.linear_model import *
from sklearn.ensemble import *
from sklearn.svm import *
from sklearn.neighbors import *

TYPE = 'type'
BBO = 'BBO'
TRADE = 'TRADE'


def gen_features(records):
  trades = sorted([r for r in records if r.key['type'] == 'TRADE'], key=lambda t: t.key['time'])
  times = [t.key['time'] for t in trades]
  tradePrices = [float(t.key['lastPrice']) for t in trades if t.key['type'] == 'TRADE']
  priceImproved = list()
  for i in range(0, len(tradePrices)):
    price_improvement = False
    i_min = min(i+1, len(tradePrices))
    i_max = min(i+3, len(tradePrices))
    future_prices = tradePrices[i_min:i_max]
    if len(future_prices) > 0 and (sum(future_prices)/len(future_prices)) > tradePrices[i]:
      price_improvement = True
    priceImproved.append(price_improvement)
  avg5Prices = list()
  prevPrices = list()
  currentPrices = list()
  for i in range(5,len(tradePrices)):
    avg5Prices.append(sum(tradePrices[i-5:i])/5)
    prevPrices.append(tradePrices[i-1])
    currentPrices.append(tradePrices[i])
  truncatedPriceImproved = priceImproved[5:]
  features = np.array([avg5Prices,prevPrices,currentPrices]).T
  targets = np.array(truncatedPriceImproved)
  return features, targets

couchdb_server = couchdb.client.Server('http://localhost:5984/')
cdb = couchdb_server['hackathon']

symbols = ['AAPL','AMD','BAC', 'BMY', 'C', 'CSCO', 'CYH', 'FB', 'FCX', 'GE', 'INTC', 'MDLZ', 'MSFT', 'WMT', 'MU', 'INTC', 'PFE', 'VZ', 'WFZ', 'WMT', 'XOM']
for symbol in ['AAPL']:
  try:
    print('Loading data from couchdb for %s...' % symbol)
    current_time = time.time()*1e3
    recent_cutoff = current_time - 60*10*1e3
    old_cutoff = current_time - 60*15*1e3
    # records = sorted([x for x in cdb.query(''' function(doc) { if(doc.symbol == \'''' + symbol + '''\' && doc.time > ''' + str(int(old_cutoff)) + ''') emit(doc);} ''')], key=lambda t: t.key['time'])
    # test_records = [r for r in records if int(r.key['time']) < recent_cutoff]
    # train_records = [r for r in records if int(r.key['time']) > recent_cutoff]
    records = sorted([x for x in cdb.query(''' function(doc) { if(doc.symbol == \'''' + symbol + '''\') emit(doc);} ''')], key=lambda t: t.key['time'])
    test_records = records[0:int(len(records)/3)]
    train_records = records[int(len(records)/3):]

    if len(train_records) == 0 or len(test_records) == 0:
      print('NO DATA!!!!!!!!!!')

    print('Loaded %d training records and %d test records' % (len(train_records), len(test_records)))
    print('Generating features...')
    train_features, train_targets = gen_features(train_records)
    test_features, test_targets = gen_features(test_records)
  
    print('Training model...')
    model = LogisticRegressionCV(multi_class='multinomial')
    model.fit(train_features, train_targets)
    predictions = model.predict(test_features)
    print('Accuracy: %f' % (sum(predictions == test_targets) / predictions.shape[0]))
    print('Saving model to models/%s_lr.p' % symbol)
    joblib.dump(model, os.path.join('models', '%s_lr' % symbol))
  except RuntimeError as e:
    print(symbol)
    print(e)

