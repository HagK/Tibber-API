#!/usr/bin/env python3

import os, logging, requests, json, datetime, redis
from dotenv import load_dotenv

load_dotenv()
# create a .env file with follow variables
redisserver = os.getenv('redisserver')
redispassword = os.getenv('redispassword')
redisfallback = os.getenv('redisfallback')
redisport = os.getenv('redisport')

tomorrow = datetime.date.today() + datetime.timedelta(days=1) 
# historische fehlende Tages-Daten importieren
# tomorrow = datetime.date.today() - datetime.timedelta(days=3) 

# curl "https://api.awattar.de/v1/marketdata/?start=1526881600000&end=2696971600000" > awattar.json
# timestap in milliseconds ... data only available for +24h from now()
r = requests.get('https://api.awattar.de/v1/marketdata/?start='+tomorrow.strftime('%s')+'000')

if r.status_code == 200:
    try:
        data = json.loads(r.text)
    except Exception as E:
        logging.error(E)
else:
    logging.error(r.headers)

try:
  redis_db = redis.StrictRedis(host=redisserver, port=redisport, db=0, socket_timeout=2, password=redispassword)
except:
  logging.error("redisdb not reachable")
  redis_db = redis.StrictRedis(host=redisfallback, port=redisport, db=0, socket_timeout=2)
  pass

sum = 0
price = []
output = ''
# Iterating through the json list
for i in data['data']:
    timestamp = i['start_timestamp']/1000
    marketprice = round(i['marketprice']/1000,6)
    format_string = "%Y-%m-%d/%H"

    price.append((marketprice))
    sum += marketprice


    dt_obj = datetime.datetime.fromtimestamp(timestamp).strftime(format_string)
    # print(dt_obj)
    # my_datetime = datetime.datetime.strptime(str(dt_obj), format_string)
    output = output + (f' {dt_obj}  {marketprice}') + '\n'
    try:
        redis_db.set('eex/'+str(dt_obj), float(marketprice))
    except Exception as E:
        logging.error(E)

avg = sum / len(price)
output = 'avg ' + str(round(sum / len(price), 3)) + '     min ' + str(min(price)) + '     max ' + str( max(price)) + '\n\n' + output

print(output)