#!/usr/bin/env python

from urllib2 import urlopen
from datetime import datetime, date, timedelta
from numpy import *
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from lxml.html import parse

from matplotlib import pyplot as plt


from historicalpricedata import priceRecord, Config, yfpricedata

sp500components = map(lambda x:x.strip(), open("data/sp500.csv", 'rU'))

#timeframe = Config(date(1999, 5, 3), date(2011, 12, 5))
timeframe = Config(date(2011, 9, 1), date(2011, 12, 5))

def yfmktcap(sym):
  pg = parse("http://finance.yahoo.com/q?s=" + sym).getroot()
  sel = pg.cssselect('#yfs_j10_'+sym.lower())
  if len(sel) > 0:
    cap = sel[0].text_content() 
  else:
    print sym + " has None"
    return None
  if cap.endswith('B'):
    return float(cap.strip('B')) * 1000
  else:
    return float(cap.strip('M'))

divbb = map(lambda x:x.strip(), open('data/growthandbuyback.txt', 'r').read().split(','))

def portfolioMktWeightings(syms):
  compMktCaps = map(lambda x: yfmktcap(x), syms)
  print 'compMktCaps: ' + str(compMktCaps)
  pMktCap = sum(compMktCaps)
  return array(compMktCaps)/pMktCap
  
def priceReturn(current, original):
  return (current - original)/original

def returnSeries(config, sym):
  pd = yfpricedata(config, sym)
  sym0prices = map(lambda row: row.adj, pd)
  sym0dates = map(lambda row: row.date, pd)
  #print "Starting price: " + str(sym0prices[-1]) + " for day " + str(sym0dates[-1]) + " last price: " + str(sym0prices[0]) + " diff: " + str((sym0prices[0]-sym0prices[-1])/sym0prices[-1])
  sym0returns = map(lambda x: priceReturn(x,sym0prices[-1]), sym0prices)
  return sym0returns

def portfolioIndex(syms, config=timeframe):
  portfolioData = array(map(lambda x: returnSeries(config, x), syms)).transpose()
  mktwgts = portfolioMktWeightings(syms)
  print 'mktwgts: ' + str(mktwgts)
  return dot(portfolioData, mktwgts)[ : : -1]

def plotTS(series):
  nseries = series + 1
  plt.bar(arange(len(series)), nseries, width=1)
  plt.ylim(ymin=min(nseries))

def monthsFromBusinessDate(d, months):
  monthago = d + relativedelta(months=-months)
  delta = timedelta((monthago.weekday() + 1) % 5)
  newdate = monthago - delta
  return newdate

def standardCumulativeReturns(sym):
  monthago = date.today() + relativedelta(months=-1)
  enddate = date(monthago.year, monthago.month, monthrange(monthago.year, monthago.month)[1])
  return map(lambda months: (monthsFromBusinessDate(enddate,months), returnSeries(Config(monthsFromBusinessDate(enddate,months),enddate), sym)[0]), [1, 3, 6, 12])

# get daily price correlations for a pair of securities for a given duration
def priceCorr(cfg, symbols):
  return corrcoef(map(lambda sym: returnSeries(cfg, sym), symbols))

# There should be a way to generate this with lxml ElementFactory but the 
# library does not seem to cooperate very with map.
def htmltable(coefmtx):
  return ("".join(map(lambda row: "<tr>" + "".join(map(lambda c: "<td>" + '{0:.2f}'.format(c) + "</td>", row)) + "</tr>", coefmtx)))

def cointegration_coeff(s0, s1):
  return cov(s0, s1)/var(s1)

def cointegratability(s0, s1):
  coeff = cointegration_coeff(s0, s1)[0][1]
  d0 = array(s0) - coeff*array(s1) 

def corrSeries(returns0, returns1, period):
  numPeriods = len(returns0) / period
  series = []
  for i in range(numPeriods):
    series.append(corrcoef(returns0[i:i+period], returns1[i:i+period])[0][1])
  return series      
