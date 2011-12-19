#!/usr/bin/env python

# historicalpricedata.py
# Marshal historical price data from Yahoo Finance source
# to a Python object format
# Author: George Kuan

import csv
import math
import multiprocessing
from urllib2 import urlopen
from datetime import datetime, date, timedelta
from numpy import *
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from lxml.html import parse

class priceRecord:
  def __init__(self, date, open, high, low, close, volume, adj):
    self.date = date
    self.open = open
    self.high = high
    self.low = low
    self.close = close
    self.volume = volume
    self.adj = adj
  def __str__(self):
    return str(self.date) + " " + str(self.adj)
  def __repr__(self):
    return repr(self.date) + " " + repr(self.adj)

class Config:
  def __init__(self, startdate=date.today(), enddate=date.today()):
    self.startdate = startdate
    self.enddate = enddate

class configDuration(Config):
  def __init__(self, duration, enddate=date.today()):
    self.enddate = enddate
    self.startdate = self.enddate - timedelta(duration) - timedelta(2*(duration / 5)) 
  
def yfpricedata(config, sym):
  startdate=config.startdate
  enddate=config.enddate
  # A gotcha is that YF months are zero-origin
  raw = csv.reader(urlopen("http://ichart.finance.yahoo.com/table.csv?s=" + sym + "&a=" + str(startdate.month-1) + "&b=" + str(startdate.day) + "&c=" + str(startdate.year) + "&d=" + str(enddate.month-1) + "&e=" + str(enddate.day) + "&f=" + str(enddate.year) + "&g=d&ignore=.csv"))   
  raw.next()
  pricerecs = [ priceRecord(datetime.strptime(row[0], "%Y-%m-%d"), float(row[1]), float(row[2]), float(row[3]), float(row[4]), int(row[5]), float(row[6])) for row in raw]
  return pricerecs
