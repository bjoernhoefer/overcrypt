import os
import json
import ccxt
import paho.mqtt.client as mqtt

from forex_python.converter import CurrencyRates

# Developement Options
# devon = True
devon = False 

def on_connect(client, userdata, flags, rc):
 client.subscribe("crypto/read/agent/#")

def readcrypto(client, userdata, msg):



 cryptodata = {}
 totalfiat = 0
 for root, directories, filenames in os.walk('/etc/overcrypt'):
  for filename in filenames:
   exchange=os.path.splitext(filename)[0]
   if devon:
    print "Exchange: " + exchange
   fullpath = root+'/'+filename
   apidata = json.load(open(fullpath))
 
   if exchange == "kraken":
    api = ccxt.kraken({
     'apiKey': apidata["apiKey"],
     'secret': apidata["secret"]
    })
   elif exchange == "bitfinex":
    api = ccxt.bitfinex({
     'apiKey': apidata["apiKey"],
     'secret': apidata["secret"]
    })
    btceuro=float(api.fetch_ticker('BTC/EUR')['info']['last_price'])
   elif exchange == "binance":
    api = ccxt.binance({
     'apiKey': apidata["apiKey"],
     'secret': apidata["secret"]
    })
    c = CurrencyRates()
    dollarrate = c.get_rate('USD', 'EUR')
   else:
    print "currently not supported exchange - feel free to implement it"

   

   balance=api.fetch_balance()
   balance_total=balance['total']
   for key,value in balance_total.iteritems():
    if value > 0:
     if devon:
      print key," ",value
     if key != 'EUR':
      if exchange == "kraken":
       rate=api.fetch_ticker(key+"/EUR")
       amount = rate['last']*value
      elif exchange == "bitfinex":
       if key != 'BTC':
        btcamount=float(api.fetch_ticker(key+"/BTC")['info']['last_price'])
        btcvalue=btcamount * value
       else:
        btcvalue=value
       amount=btcvalue * btceuro

      elif exchange == "binance":
       if key == 'ETH':
        fiat_direct = True
       elif key == 'BTC':
        fiat_direct = True
       elif key == 'LTC':
        fiat_direct = True
       else:
        fiat_direct = False

       if fiat_direct:
        rate=float(api.fetch_ticker(key+"/USDT")['info']['lastPrice'])
        dollaramount=rate * value
        amount=dollaramount * dollarrate
        if devon:
         print "FIAT direct - EUR: ",amount
       else:
        btcamount=float(api.fetch_ticker(key+"/BTC")['info']['lastPrice'])
        rate=float(api.fetch_ticker("BTC/USDT")['info']['lastPrice'])
        dollaramount = rate * btcamount
        amount = dollaramount * dollarrate
       
       eurovalue = amount * dollarrate
       
       if devon:
        print "Amount in USD: ",dollaramount
        print "1 Dollar in Euro: ",dollarrate
        print "Amount in Euro: ", amount

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
