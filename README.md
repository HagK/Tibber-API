# Tibber-API

i will spread my API scripts to make my live easier
my standard tools:
* redis
* mosquitto /mqtt @victron
* python3 (i use still *copy* for compatibility)

## tibber prices today
* is a daily plaintext email to adjust your power consumption over the day
* list the costs and consumption of last days
* this script requires **redis** (w/o an exception was logged) to store consumption data
```
avg 0.336     min 0.2635     max 0.424

### expensive ###
0.392   08:00:00... 116.7%
0.414   09:00:00... 123.5%
0.406   10:00:00... 120.9%
0.404   11:00:00... 120.2%
0.384   12:00:00... 114.4%
0.388   16:00:00... 115.5%
0.424   17:00:00... 126.4%
0.386   18:00:00... 115.2%

### cheapest 03:00:00 ###
0.272   01:00:00 CHEAP 80.9%
0.267   02:00:00 CHEAP 79.7%
0.264   03:00:00 CHEAP 78.5%
0.264   04:00:00 CHEAP 78.6%
0.271   05:00:00 CHEAP 80.8%

### next cheapest hour: 00:00:00
0.277   00:00:00 CHEAP 82.5%

### consumption/costs last 4 days:
2023-11-27   3.573 kWh   1.018
2023-11-28   7.337 kWh   2.051
2023-11-29   21.432 kWh   5.619
2023-11-30   6.718 kWh   1.945
```

## awattar.py

To have an idea of next day prices, i use awattar-API, because the API of tibber for prices_tomorrow often results in HTTP/200 with empty content.
This EEX price is without tax, this result in an offset of 0,15 - 0,2 €
The output is only on stdout and also **redis** will be filled with results.
```
avg 0.105     min 0.08886     max 0.12905

 2023-12-03/00  0.1083
 2023-12-03/01  0.10268
 2023-12-03/02  0.09988
 2023-12-03/03  0.09862
 2023-12-03/04  0.09462
 2023-12-03/05  0.09172
 2023-12-03/06  0.08886
 2023-12-03/07  0.09213
 2023-12-03/08  0.09702
 2023-12-03/09  0.10015
 2023-12-03/10  0.10496
 2023-12-03/11  0.10507
 2023-12-03/12  0.10291
 2023-12-03/13  0.1
 2023-12-03/14  0.10568
 2023-12-03/15  0.115
 2023-12-03/16  0.1222
 2023-12-03/17  0.1279
 2023-12-03/18  0.12905
 2023-12-03/19  0.12607
 2023-12-03/20  0.11233
 2023-12-03/21  0.1
 2023-12-03/22  0.09909
 2023-12-03/23  0.089
```
