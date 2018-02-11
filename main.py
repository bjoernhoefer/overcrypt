import os
import json
import ccxt
import paho.mqtt.client as mqtt

from forex_python.converter import CurrencyRates

# Developement Options
# devon = True
devon = False 
# moredev = True
moredev = False
# mostdev =True
mostdev= False


# General Settings: (currently not active/supported)
# BTC-Exchange = True
# ETH-Exchange = True
bestpriceing = True
# bestpriceing = False


def on_connect(client, userdata, flags, rc):
 client.subscribe("crypto/read/agent/#")

def marketdatawork( api, key, value, apiversion, exchange_currency, lastpricevar ):
 fiat_direct = False
 btc_trade = False
 eth_trade = False
 if bestpriceing:
  bestprice = []

 if moredev:
  print "API version:",apiversion

#### API Versin 0 (kraken)
 if apiversion == "v0":
  markets = api.load_markets()
  if mostdev:
   print json.dumps(markets) 
  for pair in markets:
   if markets[pair]['base'] == key:
    if markets[pair]['quote'] == exchange_currency:
     if devon:
      print "Direct convertable"
     fiat_direct = True
     rate=api.fetch_ticker(key+"/"+exchange_currency)
     direct_amount = rate['last']*value
     if exchange_currency != 'EUR':
      if exchange_currency == 'USDT':
       forex_query_currency = 'USD'
      else:
       forex_query_currency = exchange_currency
      c = CurrencyRates()
      exchange_rate = c.get_rate(forex_query_currency, 'EUR')
      exchange_amount = direct_amount * exchange_rate
      if devon:
       print "Direct convertable - Exchange amount - ",exchange_currency,":",exchange_amount
     else:
      exchange_amount = direct_amount
      if devon:
       print "Direct convertable - Exchange amount - ",exchange_currency,":",exchange_amount
     if bestpriceing:
      bestprice.append(exchange_amount)
    else:
     if mostdev:
      print "Not direct convertable"
### Convert to BTC
     if markets[pair]['quote'] == "BTC":
      if devon:
       print "Not direct convertable - BTC"
      btc_trade = True
      btc_amount_rate=api.fetch_ticker(key+"/BTC")
      btc_amount = btc_amount_rate['last']*value

      # btc_forex_rate = api.fetch_ticker("BTC/"+exchange_currency)
      btc_forex_rate = api.fetch_ticker("BTC/"+exchange_currency)
      btc_forex = float(btc_forex_rate['last'])
      forex_amount = btc_amount * btc_forex
      if exchange_currency != 'EUR':
       if exchange_currency == 'USDT':
        forex_query_currency = 'USD'
       else:
        forex_query_currency = exchange_currency
       c = CurrencyRates()
       exchange_rate = c.get_rate(forex_query_currency, 'EUR')
       exchange_amount = forex_amount * exchange_rate
      else:
       forex_query_currency = exchange_currency
       exchange_amount = forex_amount
      if devon:
       print "BTC Amount:",btc_amount,"-",exchange_currency,"Amount:",forex_amount,"- EUR Amount:",exchange_amount
      if bestpriceing:
       bestprice.append(exchange_amount)

### Convert to ETH
     if markets[pair]['quote'] == "ETH":
      if devon:
       print "Not direct convertable - ETH"
      eth_trade = True
      eth_amount_rate=api.fetch_ticker(key+"/ETH")
      eth_amount = eth_amount_rate['last']*value
      eth_forex_rate = api.fetch_ticker("BTC/"+exchange_currency)
      eth_forex = float(eth_forex_rate['last']*eth_amount)
      forex_amount = eth_amount * btc_forex
      if exchange_currency != 'EUR':
       if exchange_currency == 'USDT':
        forex_query_currency = 'USD'
       else:
        forex_query_currency = exchange_currency
       c = CurrencyRates()
       exchange_rate = c.get_rate(forex_query_currency, 'EUR')
       exchange_amount = forex_amount * exchange_rate
      else:
       forex_query_currency = exchange_currency
       exchange_amount = forex_amount
      if devon:
       print "ETH Amount:",btc_amount,"-",exchange_currency,"Amount:",forex_amount,"- EUR Amount:",exchange_amount
      if bestpriceing:
       bestprice.append(exchange_amount)

### Amount - Decide what to use
     else:
      if fiat_direct:
       if moredev:
        print "Amount - Using direct conversion"
       amount = exchange_amount
      elif btc_trade:
       if moredev:
        print "Amount - Using BTC conversion"
       amount = exchange_amount
      elif eth_trade:
       if devon:
        print "Amount - Using ETH conversion"
       amount = exchange_amount

### API Version 2

 if apiversion == "v2":
  markets = api.load_markets()
  if mostdev:
   print json.dumps(markets) 
  for pair in markets:
   if markets[pair]['base'] == key:
    if markets[pair]['quote'] == exchange_currency:
     if devon:
      print "Direct convertable"
     fiat_direct = True
     exchange_amount = float(api.fetch_ticker(key+"/"+exchange_currency)['info'][lastpricevar]) * value
     if devon:
      print "Direct convertable - Exchange amount - ",exchange_currency,":",exchange_amount
     if bestpriceing:
      bestprice.append(exchange_amount)
    else:
     if devon:
      print "Not direct convertable"

### Convert to BTC
     if markets[pair]['quote'] == "BTC":
      if devon:
       print "Not direct convertable - BTC"
      btc_trade = True
      btc_amount = float(api.fetch_ticker(key+"/BTC")['info'][lastpricevar]) * value
      btc_forex = float(api.fetch_ticker("BTC/"+exchange_currency)['info'][lastpricevar])
      forex_amount = btc_amount * btc_forex
      if exchange_currency != 'EUR':
       if exchange_currency == 'USDT':
        forex_query_currency = 'USD'
       else:
        forex_query_currency = exchange_currency
       c = CurrencyRates()
       exchange_rate = c.get_rate(forex_query_currency, 'EUR')
       exchange_amount = forex_amount * exchange_rate
      else:
       forex_query_currency = exchange_currency
       exchange_amount = forex_amount
      if devon:
       print "BTC Amount:",btc_amount,"-",exchange_currency,"Amount:",forex_amount,"- EUR Amount:",exchange_amount
      if bestpriceing:
       bestprice.append(exchange_amount)

#### Convert it to ETH
     if markets[pair]['quote'] == "ETH":
      if devon:
       print "Not direct convertable - ETH"
      eth_trade = True
      eth_amount = float(api.fetch_ticker(key+"/ETH")['info']['lastPrice']) * value
      eth_forex = float(api.fetch_ticker("ETH/"+exchange_currency)['info'][lastpricevar])
      forex_amount = eth_amount * eth_forex
      if exchange_currency != 'EUR':
       if exchange_currency == 'USDT':
        forex_query_currency = 'USD'
       else:
        forex_query_currency = exchange_currency
       c = CurrencyRates()
       exchange_rate = c.get_rate(forex_query_currency, 'EUR')
       exchange_amount = forex_amount * exchange_rate
      else:
       forex_query_currency = exchange_currency
       exchange_amount = forex_amount
      if devon:
       print "ETH Amount:",eth_amount,"-",exchange_currency,"Amount:",forex_amount,"- EUR Amount:",exchange_amount
      if bestpriceing:
       bestprice.append(exchange_amount)

### Amount - Decide what to use
     else:
      if fiat_direct:
       if moredev:
        print "Amount - Using direct conversion"
       amount = exchange_amount
      elif btc_trade:
       if moredev:
        print "Amount - Using BTC conversion"
       amount = exchange_amount
      elif eth_trade:
       if moredev:
        print "Amount - Using ETH conversion"
       amount = exchange_amount

 if moredev:
  print "bestprice-array:",bestprice
 bestsort = sorted(bestprice)

 return bestsort[-1]

def readcrypto(client, userdata, msg):

 cryptodata = {}
 totalfiat = 0
 if devon:
  path = 'testconf'
 else:
  path = '/etc/overcrypt'
 for root, directories, filenames in os.walk(path):
  for filename in filenames:
   exchange=os.path.splitext(filename)[0]
   if devon:
    print "Exchange: " + exchange
   fullpath = root+'/'+filename
   apidata = json.load(open(fullpath))
 


### Kraken 
   if exchange == "kraken":
    api = ccxt.kraken({
     'apiKey': apidata["apiKey"],
     'secret': apidata["secret"]
    })

### Bitfinex
   elif exchange == "bitfinex":
    api = ccxt.bitfinex({
     'apiKey': apidata["apiKey"],
     'secret': apidata["secret"]
    })

### Binance
   elif exchange == "binance":
    api = ccxt.binance({
     'apiKey': apidata["apiKey"],
     'secret': apidata["secret"]
    })

### Poloinex
   elif exchange == "poloniex":
    api = ccxt.poloniex({
     'apiKey': apidata["apiKey"],
     'secret': apidata["secret"]
    })
    
   else:
    print "currently not supported exchange - feel free to implement it"

## Fetch Balance
   balance=api.fetch_balance()
   balance_total=balance['total']
   for key,value in balance_total.iteritems():
    if value > 0:
     if devon:
      print key, value
     if key != 'EUR':

### Kraken
      if exchange == "kraken":
       amount = marketdatawork(api, key, value, "v0", "USD", "")
       
### Bitfinex
      elif exchange == "bitfinex":
       amount = marketdatawork(api, key, value, "v2", "USD", "last_price")

### Binance
      elif exchange == "binance":
       amount = marketdatawork(api, key, value, "v2", "USDT", "lastPrice")
      elif exchange == "poloniex":
       amount = marketdatawork(api, key, value, "v2", "USDT", "last")

## Create Transaction-Data
     if key in cryptodata:
      cryptodata[key]['amount'] += value 
      cryptodata[key]['fiat'] += amount
      cryptodata[key]['informationtyp'] = "single"
      cryptodata[key]['source'] = "multi"
     else:
      cryptodata[key] = {}
      cryptodata[key]['amount'] = value
      cryptodata[key]['fiat'] = amount
      cryptodata[key]['informationtyp'] = "single"
      cryptodata[key]['source'] = exchange
     totalfiat += amount
     if devon:
      print "Totalfiat: ",totalfiat

 totaldata = {}
 totaldata['amount'] = totalfiat
 totaldata['currency'] = "EUR"
 totaldata['informationtype'] = "total"
 totaldata['source'] = "multi"
 if not devon:
  client.publish("crypto/write/agent", json.dumps(totaldata))
      
 for data in cryptodata.iteritems():
  transmitdata = {}
  transmitdata['currency'] = data[0]
  transmitdata['amount'] = data[1]['amount']
  transmitdata['fiat_currency'] = "EUR"
  transmitdata['fiat_amount'] = data[1]['fiat']
  transmitdata['informationtyp'] = data[1]['informationtyp']
  transmitdata['source'] = data[1]['source']
  if not devon:
   client.publish("crypto/write/agent", json.dumps(transmitdata))

client = mqtt.Client()
client.on_connect = on_connect

client.message_callback_add('crypto/read/agent', readcrypto)

client.connect("mqtt", 1883, 60)

client.loop_forever()

