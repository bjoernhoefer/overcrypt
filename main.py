import os
import json
import ccxt
import paho.mqtt.client as mqtt

# cryptodata = {}
# totalfiat = 0

def on_connect(client, userdata, flags, rc):
 client.subscribe("crypto/read/agent/#")

def readcrypto(client, userdata, msg):
 cryptodata = {}
 totalfiat = 0
 for root, directories, filenames in os.walk('/etc/overcrypt'):
  for filename in filenames:
   exchange=os.path.splitext(filename)[0]
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
   else:
    print "currently not supported exchange - feel free to implement it"

   balance=api.fetch_balance()
   balance_total=balance['total']
   for key,value in balance_total.iteritems():
    if value > 0:
     if key != 'EUR':
      if exchange == "kraken":
       rate=api.fetch_ticker(key+"/EUR")
       amount = rate['last']*value
      elif exchange == "bitfinex":
       btcamount=float(api.fetch_ticker(key+"/BTC")['info']['last_price'])
       btcvalue=btcamount * value
       amount=btcvalue * btceuro
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

# print totalfiat
 
 totaldata = {}
 totaldata['amount'] = totalfiat
 totaldata['currency'] = "EUR"
 totaldata['informationtype'] = "total"
 totaldata['source'] = "multi"
 client.publish("crypto/write/agent", json.dumps(totaldata))
      
 for data in cryptodata.iteritems():
  transmitdata = {}
  transmitdata['currency'] = data[0]
  transmitdata['amount'] = data[1]['amount']
  transmitdata['fiat_currency'] = "EUR"
  transmitdata['fiat_amount'] = data[1]['fiat']
  transmitdata['informationtyp'] = data[1]['informationtyp']
  transmitdata['source'] = data[1]['source']
  # print transmitdata
  client.publish("crypto/write/agent", json.dumps(transmitdata))
 
client = mqtt.Client()
client.on_connect = on_connect

client.message_callback_add('crypto/read/agent', readcrypto)

client.connect("mqtt", 1883, 60)

client.loop_forever()


