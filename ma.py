#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import time
import sys
import urllib2

fee = 0.002

ma_size = 5 # 均线类型，默认是ma5，也可自定义其他

market = sys.argv[1] # 币种
step = int(eval(sys.argv[2]) * 60) # 周期
start_time = long(sys.argv[3]) # 回测起始时间
end_time = long(sys.argv[4]) # 回测结束时间

#####################数据从sosobtc获得#####################
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
f = opener.open('https://k.sosobtc.com/data/period?symbol=' + market + '&step=' + str(step))
k = f.readline()

sticks = json.loads(k)

times = []
opens = dict()
highs = dict()
lows = dict()
closes = dict()

for stick in sticks:
    times.append(stick[0])
    opens[stick[0]] = stick[1]
    highs[stick[0]] = stick[2]
    lows[stick[0]] = stick[3]
    closes[stick[0]] = stick[4]

#####################初始化均线#####################
ma_line = dict()
for i in range(len(times)):
    ma_len = ma_size
    if i + 1 < ma_size:
        ma_len = i + 1

    ma = 0
    for j in range(ma_len):
        t = times[i - j]
        ma += closes[t]

    ma = ma / ma_len
    ma_line[times[i]] = ma

init_asset = 10000
asset = init_asset

cny = init_asset
coins = 0
pre_price = 0

#####################开始回测#####################
for i in range(len(times)):
    if i == 0:
        continue

    prev_time = times[i - 1]
    cur_time = times[i]
    if cur_time < start_time:
        continue

    if cur_time > end_time:
        break

    if cur_time not in ma_line.keys():
        continue

    pre_price = closes[prev_time]

    lt = time.localtime(cur_time)
    str_time = time.strftime('%Y-%m-%d', lt)

    buy_price = opens[cur_time]
    sell_price = opens[cur_time]

    if ma_line[prev_time] < pre_price and cny > 0: # 如果突破均线, 且还有法币，全仓买入
        coins = (1 - fee) * cny / buy_price
        asset = cny * (1 - fee)
        cny = 0

        print('' + str_time + "买入, 价格: " + str(buy_price) + ", 当前资产: " + str(asset))

    if ma_line[prev_time] > pre_price and coins > 0: # 如果跌破均线，且还有币，则卖出
        cny = (1 - fee) * coins * sell_price
        asset = cny
        coins = 0

        print('' + str_time + "卖出, 价格: " + str(sell_price) + ", 当前资产: " + str(asset))


#####################打印资产#####################
asset = cny + coins * pre_price

print('\n最新价格: ' + str(pre_price) + ', 最初资产: ' + str(init_asset) + ', 最终资产: ' + str(asset))
