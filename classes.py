from __future__ import print_function
import httplib
import urllib
import json
import sys
import time
import datetime
import requests
import collections
from time import gmtime, strftime

#nohup python oanda-autotrader.12.py &> trader.log&
#trader.log will be created and "kill [PID]" to stop oanda process in background.

class Server:
  'Will hold a list of currency objects and perform operations on them, while also updating a bank object.'
  'No Global Variables for this class'
  def __init__(self, Currencies):
    self.Currencies = Currencies
  def updatePairs(self, Currencies):
    self.Currencies = Currencies
    print("will update the current server's currency list with an updated version. i.e as more historical data is processed.")
  def checkRisk(self):
    print("Function that will check the Bank Object for the risk amount and if too much has been lost.")

  def makeTrade(self, pair):
    print("Will get the index of the pair in the Currencies list and perform a trade.")

  def processResults(self, Currencies):
    print("Will get the results of a trade and update the bank balance - future to update if a trend was gained or lost")


class Bank:
  'Will have the balance and percent risk, only 1 object is necssary of this class'
  balance = 0
  percent_risk = 0    #In percent
  def __init__(self, balance, percent_risk):
    Bank.balance = balance
    Bank.percent_risk = percent_risk

  def setBalance(self, balance):
    Bank.balance = balance

  def setRisk(self, risk):
    Bank.percent_risk = risk

  def calcRisk(self):
    print("Should return true or false, based on if too much money was lost > risk amount in a trading session.")


class Currency:
  'Will be a self-contained currency pair object - Starts as Uptrend true and an empty timeSet dictionary'
  'No Global Variables'
  def __init__(self, pair, period, granularity, trend=5, timeSet={}):
    #pair is a string, period and granularity are ints, '
    #timeSet is a Dictionary mapping the date as key, and highAsk, lowAsk as values.'
    #uptrend is a booleanm, where true = uptrend, false = downtrend
    self.pair = pair
    self.period = period
    self.granularity = granularity
    self.timeSet = timeSet
    self.trend = trend

  def setTimeSet(self, timeSet):
    self.timeSet = timeSet

  def setTrend(self, uptrend):
    self.trend = trend

  def setPair(self, pair):
    self.pair = pair

  def setPeriod(self, period):
    self.period = period

  def setGranularity(self, granularity):
    self.granularity = granularity

#Will populate the timeSet dictionary parameter with data from the past 'period' days.
  def fillTimeSet(self, period, granularity):
        url = "https://api-fxpractice.oanda.com/v1/candles?count=" + str(period) + "&instrument=" + self.pair +"&granularity=" + str(granularity) + "&candleFormat=bidask"
        header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer ffc65942bd830f2cf8867a57a8e548e3-c269c756a553957fc32c985e7f0e02d6", "Accept-Encoding": "gzip, deflate"}
        connect = requests.get(url, headers=header, verify=False)
        jsoncandle = connect.json()
        #print(jsoncandle)
        candles = jsoncandle['candles']
        #Fills out the TimeSet dictionary with the closeAsk, highAsk and lowAsk prices as a list of values associated with the date as the key.
        for i in range(0, period):
            self.timeSet[candles[i]['time']] = [ candles[i]['closeAsk'], candles[i]['highAsk'], candles[i]['lowAsk'] ]
        print(self.timeSet.keys())


  ## Calculates the SMA over 'period' candles of size 'granularity' for pair 'pair'
  def SMA(self, period, granularity):
   # conn = httplib.HTTPSConnection("api-fxpractice.oanda.com")
   # url = ''.join(["/v1/candles?count=", str(period + 1), "&instrument=", pair, "&granularity=", str(granularity), "&candleFormat=bidask"])
   # print url
   # conn.request("GET", url)
   # response = conn.getresponse().read()
    url = "https://api-fxpractice.oanda.com/v1/candles?count=" + str(period) + "&instrument=" + self.pair +"&granularity=" + str(granularity) + "&candleFormat=bidask"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header, verify=False)
 #   print("hello" + connect.text
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

  def pastSMA(self, period, granularity):
    distance_in_history = period #10 Number of periods to check back for the SMA values. ADJUST THIS VALUE!!
    candleList = []
    #for i in range(0,distance_in_history):
    url = "https://api-fxpractice.oanda.com/v1/candles?count=" + str(int(period)+distance_in_history) + "&instrument=" + self.pair +"&granularity=" + str(granularity) + "&candleFormat=bidask"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header, verify=False)
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
 #    print j
      for i in range(j, period+j):
        smaSum += candles[i]['closeAsk']
#     print smaSum, "*&********&"
      smaSum = round(smaSum / int(period), 4)
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

#Determines the trend via the 200 SMA. 5 = neutral, 0 = downtrend, 10 = uptrend
#trend > 7 = UpTrend; trend < 3 = DownTrend
  def calcTrend(self):
    pastSMA_12 = self.pastSMA(200, self.granularity)
    for i in range(0, len(pastSMA_12)-1):
      if (self.trend < 10 and self.trend > 0):
        if (pastSMA_12[i+1] > pastSMA_12[i]):
          self.trend += 1   #The next value is greater than the previous.
        elif (pastSMA_12[i+1] < pastSMA_12[i]):
          self.trend -= 1   #The next value is less than the previous.
    return self.trend
#*****NEED TO REFINE the tolerance of the SMA12 and 24.
#Determine when 12SMA and 24SMA cross.
  def findPipCross(self):
    SMA12 = self.SMA(12, self.granularity)
    SMA24 = self.SMA(24, self.granularity)
    if (self.trend > 5 and SMA24 >= (0.9*SMA12) and SMA24 <= (1.1*SMA12)):
      #This signifies a BUY Signal.
      print("Buy Now")
      return True
    elif (self.trend < 5 and SMA24 >= (0.9*SMA12) and SMA24 <= (1.1*SMA12)):
      #This signifies a SELL Signal.
      print("Sell Now")
      return False
    else:
      return

#For now, this function will be used to determine the stop and limit amounts for EntryPoint() above. Future: Only buy/sell if the resiustance/support values are hit 2-3 times in the last period.
def SupportandResistance(pair, granularity):
    searchBuffer = 15
    count = 0
    url = "https://api-fxpractice.oanda.com/v1/candles?count=" + str(searchBuffer) + "&instrument=" + pair +"&granularity=" + str(granularity) + "&candleFormat=bidask"
    header = {"Content-Type" : "application/x-www-form-urlencoded", "Authorization" : "Bearer key", "Accept-Encoding": "gzip, deflate"}
    connect = requests.get(url, headers=header, verify=False)
    jsoncandle = connect.json()
    candles = jsoncandle['candles']
    lastHigh = candles[count]['highAsk']
    lastLow = candles[count]['lowAsk']
    #Find the highest high and lowest low over the past "searchBuffer" candles of candleWidth "granularity"
    for i in range(searchBuffer-1):
        count = count + 1
        if float(candles[count]['highAsk']) >= float(lastHigh):
            lastHigh = candles[count]['highAsk']
     #       print("changedHHHH: ", lastHigh, candles[count-1]['highAsk']
        if candles[count]['lowAsk'] <= float(lastLow):
            lastLow = candles[count]['lowAsk']
     #       print("changedLLLL: ", lastLow, candles[count-1]['lowAsk']
    #Compare the highest high and lowest low obtain above with the data, again, this time accept candles within (high-low/5 pips above or below). Future: This will be used to better
    # speculate signals based on the amount of times the support/resistance level has been hit (given by the length of highList and lowList below).
    for candle in candles:
        candleBuffer = ((lastHigh - lastLow)) * 0.0001 #Careful if trading USD/JPY here.
        highList = [lastHigh]
        lowList = [lastLow]
      #  print("high: ", candle['highAsk']
      #  print("low: ", candle['lowAsk']
        if (lastHigh - int(candle['highAsk'])) / 0.0001 >= candleBuffer:
            highList = highList + [candle['highAsk']]
        if (int(candle['lowAsk']) - lastLow) / 0.0001 <= candleBuffer:
            lowList = lowList + [candle['lowAsk']]

    eprint("lastHigh:", lastHigh)
    eprint("lastLow:", lastLow)
   # print("highList:", highList
   # print("lowList:", lowList

    return (lastHigh,lastLow)


