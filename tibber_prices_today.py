#!/usr/bin/env python3
import os, sys, time, datetime, json, copy, logging
import smtplib
import requests
import redis
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
# create a .env file with follow variables
apiuri = os.getenv('tibberapiuri')
auth = 'Bearer ' + str(os.getenv('tibberauth'))
costshistory = os.getenv('tibbercostshistory')
redisserver = os.getenv('redisserver')
redispassword = os.getenv('redispassword')
redisfallback = os.getenv('redisfallback')
redisport = os.getenv('redisport')

send_to =  os.getenv('send_to')
# later sendouts to other family members
if int(datetime.datetime.now().strftime("%H")) > 4:
    send_to = os.getenv('send_to2')
send_from = os.getenv('send_from')
send_via = os.getenv('send_via')

pricesquery = {"query": "{viewer {homes {subscriptions {priceInfo {today {startsAt total level} } }}}}"}
costsquery = {"query": "{viewer {homes {id consumption(resolution: DAILY, last: " + str(costshistory) + ") {nodes {from to cost unitPrice unitPriceVAT consumption} }}}}"}
headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": str(auth)}

if len(redisserver) > 3:
    try:
        redis_db = redis.StrictRedis(host=redisserver, port=redisport, db=0, password=redispassword)
    except:
        logging.error("redisdb not reachable")
        redis_db = redis.StrictRedis(host=redisfallback, port=redisport, db=0)
        pass

output = ''

def sendEmail(message):
    # Create a text/plain message
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = 'tibber prices today ' + str(datetime.date.today())
    msg['From'] = send_from
    msg['To'] = send_to
    # Send the message via our own SMTP server.
    s = smtplib.SMTP(send_via)
    s.send_message(msg)
    s.quit()

def capturePrices():
    lenprices = 0
    iterate = 0
    prices = []
    while lenprices == 0:
        r = requests.post(apiuri, headers=headers, json=pricesquery)
        curlrc = r.status_code
        try:
            content = json.loads(r.text)
            # prices = content['data']['viewer']['homes'][0]['subscriptions'][0]['priceInfo']['tomorrow']
            prices = content['data']['viewer']['homes'][0]['subscriptions'][0]['priceInfo']['today']
            lenprices = len(prices)
        except Exception as E:
            logging.error(E)
        if lenprices == 0:
            if iterate > 30:
                sys.exit('error - no prices available - curlRC:' + str(curlrc) + ' curl iteration: ' +str(iterate))
            else:
                iterate = iterate + 1
                time.sleep(321)
    return prices

def captureCosts():
    costs = []
    r = requests.post(apiuri, headers=headers, json=costsquery)
    if r.status_code != 200:
        return costs
    try:
        content = json.loads(r.text)
        costs = content['data']['viewer']['homes'][0]['consumption']['nodes']
    except Exception as E:
        logging.error(E)
    return costs

sum = 0
price = []
prices = capturePrices()
sumtwo = 0
pricetwo = []
pricestwo = copy.copy(prices)

for i in prices:
    price.append((i['total']))
    len(price)
    sum += i['total']

avg = sum / len(prices)
output = output +  'avg ' + str(round(sum/len(prices), 3)) + '     min ' + str(min(price)) + '     max ' + str(max(price)) +'\n'

output = output +  '\n### expensive ###\n'
for i in prices:
    if float(i['total']) > float(avg * 1.1):
        output = output +  f'{i["total"]:.3f}' + '   '+str(i['startsAt'][11:-10])+'... '+str(round(float(i['total']*100) / float(avg), 1))+'% \n'

indexmin = price.index(min(price))


# remove cheapest prices from pricestwo
try:
  if indexmin > 1:
    for i in [1, 2, 3, 4, 5]:
      try:
        pricestwo.pop(indexmin -2)
      except:
        pass
  elif indexmin > 0:
    for i in [1, 2, 3, 4]:
      try:
        pricestwo.pop(indexmin -1)
      except:
        pass
  else:
      pricestwo.pop(indexmin)
      try:
        pricestwo.pop(indexmin)
        pricestwo.pop(indexmin)
      except:
        pass 
except:
  pass


for i in pricestwo:
    pricetwo.append((i['total']))
indexmintwo = pricetwo.index(min(pricetwo))

output = output +  '\n### cheapest ' + str(prices[indexmin]['startsAt'][11:-10]) + ' ###\n'
try:
  if indexmin > 1:
    output = output + f'{price[indexmin -2]:.3f}' + '   ' + str(prices[indexmin -2]['startsAt'][11:-10]) + ' ' + str(prices[indexmin -2]['level']) + ' ' + str(round(float(price[indexmin -2]*100)/float(avg), 1)) + '%\n'
  if indexmin > 0:
    output = output +  f'{price[indexmin -1]:.3f}' + '   ' + str(prices[indexmin -1]['startsAt'][11:-10]) + ' ' + str(prices[indexmin -1]['level']) + ' ' + str(round(float(price[indexmin -1]*100)/float(avg), 1)) + '%\n'

  output = output +  f'{price[indexmin]:.3f}' + '   ' + str(prices[indexmin]['startsAt'][11:-10]) + ' ' + str(prices[indexmin]['level']) + ' ' + str(round(float(price[indexmin]*100)/float(avg), 1)) + '%\n'

  if indexmin < 23:
    output = output + f'{price[indexmin +1]:.3f}' + '   ' + str(prices[indexmin +1]['startsAt'][11:-10]) + ' ' + str(prices[indexmin +1]['level']) + ' ' + str(round(float(price[indexmin +1]*100)/float(avg), 1)) + '%\n'
  if indexmin < 22:
    output = output + f'{price[indexmin +2]:.3f}' + '   ' + str(prices[indexmin +2]['startsAt'][11:-10]) + ' ' + str(prices[indexmin +2]['level']) + ' ' + str(round(float(price[indexmin +2]*100)/float(avg), 1)) + '%\n'

  output = output + '\n### next cheapest hour: ' + str(pricestwo[indexmintwo]['startsAt'][11:-10]) + '\n'
  output = output + f'{pricetwo[indexmintwo]:.3f}' + '   ' + str(pricestwo[indexmintwo]['startsAt'][11:-10]) + ' ' + str(pricestwo[indexmintwo]['level']) + ' ' + str(round(float(pricetwo[indexmintwo]*100)/float(avg), 1)) + '%\n'

except Exception as E:
    logging.error('indexmin ' + str(indexmin) + 'two values before/after missing')
    output = output +  str(price[indexmin]) + ' ' + str(prices[indexmin]['startsAt'][11:-10]) + ' ' + str(prices[indexmin]['level']) + '\n'
    logging.error(E)


cost = []
costs = captureCosts()
output = output + '\n\n### consumption/costs last ' + str(costshistory) + ' days: \n'
for i in costs:
    if (i['cost'] is not None and i['consumption'] is not None):
        # cost.append({"cost": i['cost'], "consumption": i['consumption'], "day": i['from'][0:10]})
        output = output + str(i['from'][0:10]) + '   ' + str(i['consumption']) + ' kWh   ' + str(round(float(i['cost']),3)) + '\n'
        try:
            redis_db.set('tibber/daily/' + str(i['from'][0:10]), float(i['consumption']))
        except Exception as E:
            logging.error(E)
            pass
    else:
        output = output + str(i['from'][0:10]) + '   ERROR MISSING DATA\n'

try:
    sendEmail(output)
except Exception as E:
    logging.error(E)
    print(output)