from __future__ import print_function
import httplib
import urllib
import json
import sys
import time
import datetime
import requests
from time import gmtime, strftime

import classes.py

#nohup python oanda-autotrader.12.py &> trader.log&
#trader.log will be created and "kill [PID]" to stop oanda process in background.

#Use eprint instead of print when printing not solely a string.
def eprint(args, kwargs):
  print(args, kwargs, file=sys.stderr)


#****CHANGES*****#
#1 Added tradeLimiter function to ensure only 1 open trade at a time for each currency pair
#2 Need to clean up Entry point and add logic for USD_JPY currency pair.





## Input Required: period granularity instrument account

## This script will constantly check for new candle information and constantly calculate SMA and WMA.
## It will then execute a trade when they cross in the appropriate direction
## For example, if the WMA grows larger than the SMA, that means price is moving up so trade long

## Parses a granularity like S10, M15, H4 into the corresponding number of seconds
## Does not take into account anything weird, leap years, DST, etc.
is_dst = time.daylight and time.localtime().tm_isdst > 0
utc_offset = (time.altzone if is_dst else time.timezone)
def getGranularitySeconds(granularity):
    if granularity[0] == 'S':
        return int(granularity[1:])
    elif granularity[0] == 'M' and len(granularity) > 1:
        return 60*int(granularity[1:])
    elif granularity[0] == 'H':
        return 60*60*int(granularity[1:])
    elif granularity[0] == 'D':
        return 60*60*24
    elif granularity[0] == 'W':
        return 60*60*24*7
    #Does not take into account actual month length
    elif granularity[0] == 'M':
        return 60*60*24*30

def pastSMA(period, pair, granularity):  
    distance_in_history = 10 #Number of periods to check back for the SMA values. ADJUST THIS VALUE!!
    candleList = []
    #for i in range(0,distance_in_history):
    url = "https://api-fxpractice.oanda.com/v1/candles?count=" + str(int(period)+distance_in_history) + "&instrument=" + pair +"&granularity=" + str(granularity) + "&candleFormat=bidask"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header)
    jsoncandle = connect.json()  
    candles = jsoncandle['candles']
    #for i in range(len(candles)):
    	#print "CNADLES: ", candles[i]['time']
    #print candles[0]['closeAsk'], "*&********&"  #List of period+i candle objects
    #del candles[:-i] #Removes first i candles from each candle list
      #Used to 'fix' the candles so that each list is the same length as the period.
    #candleList.append(candles)
   #   print len(candles), "i", i
   # print candleList
    smaList = []
    #print candles[0]['time']
    candles.reverse()
    #print candles[0]['time']
    #smaSum = 0.0
    for j in range(0, distance_in_history):
    	smaSum = 0.0
 #   	print j
    	for i in range(j, period+j):
    		smaSum += candles[i]['closeAsk']
#   	print smaSum, "*&********&"
    	smaSum = round(smaSum / int(period), 5)
    #  print "json Candle length: ", len(jsoncandle)
      #for candle in range(0,len(jsoncandle)):#-count):
        #smaSum += jsoncandle[candle]['closeAsk']
        #smaDivisor = round(smaSum / int(period), 4)
    	smaList.append(smaSum)
    smaList.reverse()
    #print smaList
    #  print count
    #  print len(jsoncandle)
     # print jsoncandle[candle]['time'], "DIVISOR", smaDivisor
   # print "LIST: ", smaList
    return smaList

## Calculates the SMA over 'period' candles of size 'granularity' for pair 'pair'
def SMA(period, pair, granularity):
   # conn = httplib.HTTPSConnection("api-fxpractice.oanda.com")
   # url = ''.join(["/v1/candles?count=", str(period + 1), "&instrument=", pair, "&granularity=", str(granularity), "&candleFormat=bidask"])
   # print url
   # conn.request("GET", url)
   # response = conn.getresponse().read()
    url = "https://api-fxpractice.oanda.com/v1/candles?count=" + str(period) + "&instrument=" + pair +"&granularity=" + str(granularity) + "&candleFormat=bidask"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header)
 #   print "hello" + connect.text
 #   print connect.json
    jsoncandle = connect.json()
   # print jsoncandle
    candles = jsoncandle['candles']
    smaSum = 0.0
    smaDivisor = 0.0
    for candle in candles:
        smaSum += candle['closeAsk']

    smaDivisor = round(smaSum / period, 4)
    return smaDivisor

#Creates a dictionary of the past 3-5 candles displaying their color, highshadow, lowshadow and bodysize in pips!
#Part of Revision 2.
def CandleAnalyze(pair, granularity):
    url = "https://api-fxpractice.oanda.com/v1/candles?count=" + str(3) + "&instrument=" + pair +"&granularity=" + str(granularity) + "&candleFormat=bidask"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header)
    jsoncandle = connect.json()
    candles = jsoncandle['candles']
    #Most Recent Candle is First!
    candleList = []
    for candle in candles:
        print(candle['time'])
        if (pair == "USD_JPY"):
            color = candleType(candle['openAsk']*0.01, candle['closeAsk']*0.01, candle['lowAsk']*0.01, candle['highAsk']*0.01)
            if color == 'red':
              highshadow = round(candle['highAsk'] - candle['openAsk'], 6) * 100
              lowshadow = round(candle['closeAsk'] - candle['lowAsk'], 6) * 100
              bodysize = round(candle['openAsk'] - candle['closeAsk'], 6) * 100
            else:
              highshadow = round(candle['highAsk'] - candle['closeAsk'], 6) * 100
              lowshadow = round(candle['openAsk'] - candle['lowAsk'], 6) * 100
              bodysize = round(candle['closeAsk'] - candle['openAsk'], 6) * 100
            candleList.append({'color':color, 'highshadow': highshadow, 'lowshadow': lowshadow, 'bodysize': bodysize})
        else:
            color = candleType(candle['openAsk'], candle['closeAsk'], candle['lowAsk'], candle['highAsk'])
            if color == 'red':
              highshadow = round(candle['highAsk'] - candle['openAsk'], 6) * 10000
              lowshadow = round(candle['closeAsk'] - candle['lowAsk'], 6) * 10000
              bodysize = round(candle['openAsk'] - candle['closeAsk'], 6) * 10000
            else:
              highshadow = round(candle['highAsk'] - candle['closeAsk'], 6) * 10000
              lowshadow = round(candle['openAsk'] - candle['lowAsk'], 6) * 10000
              bodysize = round(candle['closeAsk'] - candle['openAsk'], 6) * 10000
            candleList.append({'color':color, 'highshadow': highshadow, 'lowshadow': lowshadow, 'bodysize': bodysize})
    return candleList

  #  for item in candleList:
  #      if item == "green"

#Checks all open positions and return the amount of equity at risk, in other words, the stopLoss amount total over all open orders.
def checkOpenTrades():
    url = "https://api-fxpractice.oanda.com/v1/accounts/7079063/trades"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header)
    jsondata = connect.json()
    stopLossinUse = 0.0;
    for i in range(0,len(jsondata['trades'])):
      usedPair = jsondata['trades'][i]['instrument']
      if usedPair == "USD_JPY" or usedPair == "AUD_JPY":
        stopLossinUse += abs(jsondata['trades'][i]['stopLoss']-jsondata['trades'][i]['price']) / 0.01
      else:
        stopLossinUse += abs(jsondata['trades'][i]['stopLoss']-jsondata['trades'][i]['price']) / 0.0001
    eprint("stoploss_inuse:", stopLossinUse)
    return stopLossinUse
#1111
#Function to ensure only 1 trade is open per currency PAIR. Also checks to see if the last trade was win or loss?
def tradeLimiter(pair, pair_state):
    url = "https://api-fxpractice.oanda.com/v1/accounts/7079063/trades"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header)
    jsondata = connect.json()
    #print "HERE RESULT tradelimiter: ", jsondata['trades']
    for i in range(0,len(jsondata['trades'])):
      #print "JSON RESULT tradelimiter: ", jsondata['trades'][i]['instrument'], pair, pair_state
      if pair != jsondata['trades'][i]['instrument'] and pair_state == True: #Close out all closed trades.
        pair_state = False
        print("one boom", file=sys.stderr)
      if pair == jsondata['trades'][i]['instrument'] and pair_state == False:
        pair_state = True
        print("two boom", file=sys.stderr)
        break
      #if pair == jsondata['trades'][i]['instrument'] and pair_state == True:
      #  pair_state = True
      #  print "three boom"
    return pair, pair_state

  

#Returns true if the amount of currency put at risk ("risk_amount") is <= 1% of equity.
def equityAvailable(risk_amount):
    url = "https://api-fxpractice.oanda.com/v1/accounts/7079063"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header)
    jsondata = connect.json()
    current_equity = jsondata['balance'];
    percent_risk = 0.0008 #CHANGE to 0.01 or 1% for production!
    if (current_equity*percent_risk >= risk_amount):
   #   print "current_equity: ", current_equity*percent_risk
      eprint("risk_amount: ", risk_amount)
      return True
    elif checkOpenTrades() >= (0.05*input_balance): #(input_balance - current_equity) >= (0.05*input_balance):
      print("MAX Equity Loss Reached! Please review logs.", file=sys.stderr)
      return 0
    else:
      print("1 percent Equity in play!", file=sys.stderr)
      return False


def TrendCheck(period, pair, granularity):
    count = 0
    trend = ''
    historicalData = pastSMA(period, pair, granularity)
    for i in range(1,len(historicalData)):
      if historicalData[i] > historicalData[i-1]:
        count += 1
      elif historicalData[i] < historicalData[i-1]:
        count -= 1
  #  print count
    if count > 0:
      trend = 'up'
    elif count < 0:
      trend = 'down'
    else:
      trend = 'neutral'
   # print trend
    return trend

    #if SMA(12, granularity, pair) < SMA(24, granularity, pair):

#Up/Down trend will be dictated by a 1 or -1, where 0 is neutral. Each indicator will add or subtract .25 from the trendValue variable.
#Need to find the SMA from the past n-1 periods. Not current back 12 period, or back 24 for example!
def EntryPoint(pair, granularity, equity_at_risk):

  #****Initiate TrendCheck****
    trendFinal = "Not determined yet" #neutral as start
    smallSMA = SMA(12, pair, granularity) #the standard sma variables are the present values of the sma in integer format.
    smallSMA_his = TrendCheck(12, pair, granularity) #The _his variable should be up, down or neutral to indicate what the sma was doing previously.
   # print "SMAsmall is currently ", smallSMA, ", was previously ", smallSMA_his
    time.sleep(2)
    mediumSMA = SMA(24, pair, granularity)
    mediumSMA_his = TrendCheck(24, pair, granularity)
   # print "SMAmedium is currently ", mediumSMA, ", was previously ", mediumSMA_his
    time.sleep(2)
    largeSMA = SMA(150, pair, granularity)
    largeSMA_his = TrendCheck(100, pair, granularity)
   # print "SMAlarge is currently ", largeSMA, ", was previously ", largeSMA_his

    #Write out cases:
    #1. 12 sma greater than 24 sma, 12 is down, 24 is up, 100 sma is above 12 and 24 smas. Downtrend SELL
    #2. 24 sma greater than 12 sma, 24 is down, 12 is up, 100 sma is below 12 and 24 smas. Uptrend Buy
    #3. 12 sma less than 24 sma, 12 is up, 24 is down, 100 sma is above 12 and 24 smas. Uptrend Buy
    #4. 24 sma less than 12 sma, 24 is up, 12 is down, 100 sma is below 12 and 24 smas. Downtrend SELL
    #5. WAIT

    #****Initiate CompareTrend****
    if smallSMA < largeSMA and mediumSMA < largeSMA:
      if smallSMA > mediumSMA and smallSMA_his =='down' and mediumSMA_his == 'up':
        print("downtrend sell 1", file=sys.stderr)
        trendFinal = "down"
      elif smallSMA < mediumSMA and smallSMA_his == 'up' and mediumSMA_his == 'down':
        print("uptrend buy 2", file=sys.stderr)
        trendFinal = "up"
      elif smallSMA == mediumSMA and smallSMA_his == 'up' and mediumSMA_his == 'down':
        print("uptrend buy 3", file=sys.stderr)
        trendFinal = 'up'
      elif smallSMA > mediumSMA and smallSMA_his == 'down' and mediumSMA_his == 'neutral':
        print("downtrend sell 4", file=sys.stderr)
        trendFinal = 'down'
    elif smallSMA > largeSMA and mediumSMA > largeSMA:
      if smallSMA < mediumSMA and smallSMA_his == 'up' and mediumSMA_his == 'down':
        print("uptrend buy 5", file=sys.stderr)
        trendFinal = "up"
      elif smallSMA > mediumSMA and smallSMA_his == 'down' and mediumSMA_his == 'up':
        print("downtrend sell 6", file=sys.stderr)
        trendFinal = "down"
      elif smallSMA == mediumSMA and smallSMA_his == 'down' and mediumSMA_his == 'up':
        print("downtrend sell 7", file=sys.stderr)
        trendFinal = 'down'
      elif smallSMA < mediumSMA and smallSMA_his == 'up' and mediumSMA_his == 'neutral':
        print("uptrend buy 8", file=sys.stderr)
        trendFinal = 'up'

    eprint("trendFinal: ", trendFinal)
    myhigh, mylow = SupportandResistance(pair, granularity)

#Small widget to get the amount of pips to resistance and support from the current price.
#****Initiate PipConvert****
    url = "https://api-fxpractice.oanda.com/v1/prices?instruments=" + pair
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect2 = requests.get(url, headers=header)
    jsoncandle = connect2.json()
    currentCandle = jsoncandle['prices']
    if pair == "USD_JPY":
      distance_to_resistance = (myhigh - currentCandle[0]['ask']) / 0.01
      distance_to_support = (currentCandle[0]['ask'] - mylow) / 0.01
    else:
      distance_to_resistance = (myhigh - currentCandle[0]['ask']) / 0.0001
      distance_to_support = (currentCandle[0]['ask'] - mylow) / 0.0001
    eprint("CurrentPRICE: ", currentCandle[0]['ask'])
    #eprint(checkOpenTrades())

#****Initiate checkOpenTrades****
  #  checked_equity = checkOpenTrades()
  #  print checked_equity

#****Initiate BuyAndSell****
    #eprint("trend_decision:", trendFinal)
    equity_at_risk = checkOpenTrades()  #Update current equity at risk.
#MAIN check for intercepting small and medium SMA lines. Also make sure equity available to place trade. Wait 60 seconds after check.
    #print("COMPARING: " + str(smallSMA) + str(mediumSMA) + str(smallSMA) <= mediumSMA*1.001 and smallSMA >= mediumSMA*0.009) #Within 10% of each SMA for obtaining more "hits"
    #eprint("MED first: ", mediumSMA <= smallSMA*1.001 and mediumSMA >= smallSMA*0.009)
    if equityAvailable(equity_at_risk) and smallSMA <= mediumSMA*1.001 and smallSMA >= mediumSMA*0.009:   #1 loop
      if trendFinal == 'up':
        print("buy", file=sys.stderr)
        url = "https://api-fxpractice.oanda.com/v1/accounts/7079063/orders"
        header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
        data = ({"instrument": pair, 
          "units": 10000,
          "side": "buy",
          "takeProfit": round(myhigh*1.001, 4),
          "stopLoss": mylow,
          "type": "market"})
     
#      print "buying"
        print(data, " + ", url, file=sys.stderr)
        connect = requests.post(url, data=data, headers=header)
        print(connect.text, file=sys.stderr)
        equity_at_risk += distance_to_support #increment the equity at risk based on the amount of stoploss. 
        print(equity_at_risk)
        return equity_at_risk

      elif trendFinal == 'down':
        print("sell", file=sys.stderr)
        url = "https://api-fxpractice.oanda.com/v1/accounts/7079063/orders"
        header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
        data = ({"instrument": pair, 
          "units": 10000,
          "side": "sell",
          "takeProfit": round(mylow/1.001, 4),
          "stopLoss": myhigh,
          "type": "market"})
      
 #      print "selling"
        print(data, " + ", url, file=sys.stderr)
        connect = requests.post(url, data=data, headers=header)
        print(connect.text, file=sys.stderr)
        equity_at_risk += distance_to_resistance #increment the equity at risk based on the amount of stoploss.    
        print(equity_at_risk) 
        return equity_at_risk

      else:
        print("SMA Interception, but Insignificant Trend, so do nothing...", file=sys.stderr)
        #print "equity at risk is too great...waiting for current orders to close, EQUITY: ", equity_at_risk
        return equity_at_risk
    if equityAvailable(equity_at_risk) and mediumSMA <= smallSMA*1.001 and mediumSMA >= smallSMA*0.009:  #2 loop
      if trendFinal == 'up':
        print("buy", file=sys.stderr)
        url = "https://api-fxpractice.oanda.com/v1/accounts/7079063/orders"
        header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
        data = ({"instrument": pair, 
          "units": 10000,
          "side": "buy",
          "takeProfit": round(myhigh*1.001, 4),
          "stopLoss": mylow,
          "type": "market"})
     
#      print "buying"
        print(data, " + ", url, file=sys.stderr)
        connect = requests.post(url, data=data, headers=header)
        print(connect.text, file=sys.stderr)
        equity_at_risk += distance_to_support #increment the equity at risk based on the amount of stoploss. 
        print(equity_at_risk)
        return equity_at_risk

      elif trendFinal == 'down':
        print("sell", file=sys.stderr)
        url = "https://api-fxpractice.oanda.com/v1/accounts/7079063/orders"
        header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
        data = ({"instrument": pair, 
          "units": 10000,
          "side": "sell",
          "takeProfit": round(mylow/1.001, 4),
          "stopLoss": myhigh,
          "type": "market"})
      
 #      print "selling"
        print(data, " + ", url, file=sys.stderr)
        connect = requests.post(url, data=data, headers=header)
        print(connect.text, file=sys.stderr)
        equity_at_risk += distance_to_resistance #increment the equity at risk based on the amount of stoploss.    
        print(equity_at_risk) 
        return equity_at_risk

      else:
        print("SMA Interception, but Insignificant Trend, so do nothing...", file=sys.stderr)
        #print "equity at risk is too great...waiting for current orders to close, EQUITY: ", equity_at_risk
        return equity_at_risk
    else:
      print("No SMA Interception", file=sys.stderr)
      return equity_at_risk


#For now, this function will be used to determine the stop and limit amounts for EntryPoint() above. Future: Only buy/sell if the resiustance/support values are hit 2-3 times in the last period.
def SupportandResistance(pair, granularity):
    searchBuffer = 15
    count = 0
    url = "https://api-fxpractice.oanda.com/v1/candles?count=" + str(searchBuffer) + "&instrument=" + pair +"&granularity=" + str(granularity) + "&candleFormat=bidask"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header)
    jsoncandle = connect.json()
    candles = jsoncandle['candles']
    lastHigh = candles[count]['highAsk']
    lastLow = candles[count]['lowAsk']
    #Find the highest high and lowest low over the past "searchBuffer" candles of candleWidth "granularity"
    for i in range(searchBuffer-1):
        count = count + 1
        if float(candles[count]['highAsk']) >= float(lastHigh):
            lastHigh = candles[count]['highAsk']
     #       print "changedHHHH: ", lastHigh, candles[count-1]['highAsk']
        if candles[count]['lowAsk'] <= float(lastLow):
            lastLow = candles[count]['lowAsk']
     #       print "changedLLLL: ", lastLow, candles[count-1]['lowAsk']    
    #Compare the highest high and lowest low obtain above with the data, again, this time accept candles within (high-low/5 pips above or below). Future: This will be used to better 
    # speculate signals based on the amount of times the support/resistance level has been hit (given by the length of highList and lowList below).
    for candle in candles:
        candleBuffer = ((lastHigh - lastLow)) * 0.0001 #Careful if trading USD/JPY here.
        highList = [lastHigh]
        lowList = [lastLow]
      #  print "high: ", candle['highAsk']
      #  print "low: ", candle['lowAsk']
        if (lastHigh - int(candle['highAsk'])) / 0.0001 >= candleBuffer:
            highList = highList + [candle['highAsk']]
        if (int(candle['lowAsk']) - lastLow) / 0.0001 <= candleBuffer:
            lowList = lowList + [candle['lowAsk']]

    eprint("lastHigh:", lastHigh)
    eprint("lastLow:", lastLow)
   # print "highList:", highList
   # print "lowList:", lowList

    return (lastHigh,lastLow)


#Will calculate the delta in open/close price (body of candle) & the delta of the high and low (the candle shadows).
#Need to factor in the most influental candle patterns and should return if any of the candlestick patterns are recognized.
def candleType(openPrice, closePrice, lowAsk, highAsk):
    if openPrice > closePrice:
        state = "red"
        pipDelta = str((openPrice-closePrice)/0.0001) + " pips"
    elif openPrice < closePrice:
        state = "green"
        pipDelta = str((closePrice-openPrice)/0.0001) + " pips"
    else:
        state = "doji"
        pipDelta = str((closePrice-openPrice)/0.0001) + " pips"
    eprint("open/close diff: ", pipDelta)
    return state

def calcPip(high, low, pair):
  if pair == "USD_JPY":
    return (high-low)/0.01
  else:
    return (high-low)/0.0001



if __name__ == "__main__":
  eprint("This is the main function")
