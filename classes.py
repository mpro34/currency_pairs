from __future__ import print_function
import httplib
import urllib
import json
import sys
import time
import datetime
import requests
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
  'Will be a self-contained currency pair object'
  'No Global Variables'
  def __init__(self, pair, period, granularity, timeSet, uptrend):
    #pair is a string, period and granularity are ints, '
    #timeSet is a Dictionary mapping the date as key, and highAsk, lowAsk as values.'
    #uptrend is a booleanm, where true = uptrend, false = downtrend
    self.pair = pair
    self.period = period
    self.granularity = granularity
    self.timeSet = timeSet
    self.uptrend = uptrend

  def setTimeSet(self, timeSet):
    self.timeSet = timeSet

  def setTrend(self, uptrend):
    self.uptrend = uptrend

  def setPair(self, pair):
    self.pair = pair

  def setPeriod(self, period):
    self.period = period

  def setGranularity(self, granularity):
    self.granularity = granularity

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