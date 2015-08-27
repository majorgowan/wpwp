import requests
import datetime
import numpy
from lxml import html
from HTMLParser import HTMLParser

#------------- subclass HTMLParser to extract station data
class MyHTMLParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.recording = 0
		self.data = []

	def handle_starttag(self, tag, attrs):
		if tag=='td':
			#print "Recording? " + `self.recording`
			#print "Encountered a start tag:", tag
			self.data.append(u'NA')
			self.recording += 1

	def handle_endtag(self, tag):
		if tag=='td': 
			#print "Recording? " + `self.recording`
			#print "Encountered a end tag:", tag
			self.recording -= 1

	def handle_data(self, data):
		if self.recording:
			#print "Encountered some data:", data
			if data != "Legend Double Dagger":
				self.data[-1] = data

#------------- use HTML parser to download web page with day of hourly data
def readStationDay(stationID, year, month, day):
	base = "http://climate.weather.gc.ca/climateData/hourlydata_e.html"
	base = base + "?timeframe=1&Prov=ON"
	theUrl = base + "&StationID=" + `stationID` + \
			"&Year=" + `year` + \
			"&Month=" + `month` + "&Day=" + `day`
	page = requests.get(theUrl)
	#print page.text
	parser = MyHTMLParser()
	parser.feed(page.text)
	return parser

#------------- get station position and code (worked with old HTMLParser)
#def readStationCoord(data):
#	# take table data list and extract station info
#	# latitude:
#	degrees = float(data[0])
#	minutes = float(data[1])
#	seconds = float(data[3])
#	if data[5] == 'N':
#		theSign = 1
#	else:
#		theSign = -1
#	latitude = degrees + minutes/60 + seconds/3600
#	# longitude:
#	degrees = float(data[6])
#	minutes = float(data[7])
#	seconds = float(data[9])
#	if data[11] == 'W':
#		degrees = 360 - degrees
#	longitude = degrees + minutes/60 + seconds/3600
#	# elevation
#	elevation = float(data[12])
#	return {'long': round(longitude,3), \
#		'lat': round(latitude,3), \
#		'alt': round(elevation,3), \
#		'symbol': data[16]
#		}

#------------- get number of days in given month (includes leap year calculator)
def daysInMonth(year, month):
	dim = [31, 28, 31, 30, 31, 30, 31, 31,\
		30, 31, 30, 31]
	if month==2:
		# check if leap year
		if year%4 == 0 and (year%100 != 0 or year%400 == 0):
			return 29
	return dim[month-1]

#------------- convert an hour of data from raw list to dictionary
def readHour(data):
	hour = data[0]
	temp = data[1]
	dewp = data[2]
	humid = data[3]
	winddir = data[4]
	windsp = data[5]
	visible = data[6]
	press = data[7]
	hmdx = data[8]
	chill = data[9]
	weather = data[10]
	return {'hour': hour, 'temp': temp, \
		'dewp': dewp, 'humid': humid, \
		'winddir': winddir, 'windsp': windsp, \
		'visibility': visible, \
		'pressure': press, 'hmdx': hmdx, \
		'chill': chill, 'weather': weather}

#------------- read a single day of hourly data
def readDay(data):
	import re
	timePattern = re.compile('[0-9]{2}:[0-9]{2}')
	# find indices of times in data
	indices = [i for i,x in enumerate(data) \
			if timePattern.match(x)]
	hours = []
	for hour in indices:
		hours.append(readHour(data[hour:]))
	return hours

#------------- read a block of months from a single station
def readYear(stationID, year, months = (1,12)):
	date = []
	data = []
	# Toronto: stationID = 51459 (> 06/2013), 5097 (<= 06/2013)
	# Winnipeg: stationID = 51097 (> 01/2013), 3698 (<= 01/2013)
	# Vancouver: stationID = 51442 (> 06/2013), 889 (<= 06/2013)
	for month in range(months[0],months[1]+1):
		for day in range(1,daysInMonth(year,month)+1):
			stationDay = readStationDay(stationID, \
					year, month, day)
			#date.append("%d-%02d-%02d" % (year,month,day))
			date.append(datetime.date(year,month,day))
			data.append(readDay(stationDay.data))
	return date, data

#------------- write data to file
def writeToFile(station, data):
	pass

#------------- read data from file
def readFromFile(fileName):
	pass

#------------- replace missing values in vector with averages
#------------- of nearest non-missing values
#-- get last (sign=-1) or next (sign=+1) valid float in data
def nextFloat(data, index, sign):
	try:
		f = float(data[index])
		return f
	except ValueError:
		if (sign == 1 and index == len(data)-1) \
				or (sign == -1 and index == 0):
			return '9999'
		else:
			f = nextFloat(data,index+sign,sign)
			return f
#-- iterate over data and replace missing values
def removeMissing(data):
	ind = range(len(data))
	for ii in ind:
		# test if valid floating point value
		try:
			float(data[ii])
		except ValueError:
			last_float = nextFloat(data, ii, 1)
			next_float = nextFloat(data, ii, -1)
			data[ii] = str(numpy.mean([float(num) \
				for num in [last_float, next_float] \
				if num != '9999']))
	return data

#------------- construct date and time string
def makeDateTime(date, time):
	return date + ' ' + time

#------------- plot a variable over a time interval
#-- process variable
def processVariable(var,data,indices):
	# construct list for the new variable
	varlist = [hour[var] for day in data[indices[0]:indices[1]+1] for hour in day]
	# clean up date (convert to floats)
	varlist = removeMissing(varlist)
	# convert to floats
	varlist = [float(value) for value in varlist]
	return varlist
#-- generate datetime objects
def processDateTime(date, indices):
	datelist = [day for day in date[indices[0]:indices[1]+1]]
	datelist = [dayCopy for dayOfHours \
			in [24*[oneDay] for oneDay in datelist] \
			for dayCopy in dayOfHours]
	hoursInDays = (indices[1]-indices[0]+1)*range(24)
	dateTimeList = [datetime.datetime.combine(oneTime[0],datetime.time(hour=oneTime[1])) \
			for oneTime in zip(datelist,hoursInDays)]
	return dateTimeList

def plotData(date, data, var, start_date, end_date, title=''):
	import matplotlib.pyplot as plt
	import matplotlib.dates as mdates
	years = mdates.YearLocator()   # every year
	months = mdates.MonthLocator()  # every month
	daysLocator = mdates.DayLocator()  # every day
	theFormat = mdates.DateFormatter('%Y-%b')
	# find indices of start and end dates
	indices = [i for i,x in enumerate(date) \
			if x.isoformat() == start_date \
			or x.isoformat() == end_date]
	if len(indices) < 2:
		print "dates not in range"
		return -1
	else:
		print "index range plotted: ", indices
	# construct list for the plot variable
	varlist = processVariable(var,data,indices)
	# get requested times as datetime objects
	dateTimeList = processDateTime(date, indices)
	# make plot
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.grid(True)
	# ax.plot(range(len(varlist)),varlist)
	ax.plot(dateTimeList,varlist)
	ax.xaxis.set_major_locator(months)
	ax.xaxis.set_major_formatter(theFormat)
	ax.xaxis.set_minor_locator(daysLocator)
	plt.ylabel(var)
	plt.title(title)
	fig.autofmt_xdate()
	plt.show()

#------------- plot a daily statistic over a time interval
#-- compute statistic
def computeStatistic(var,stat,data,indices):
	theStat = []
	for ind in range(indices[0],indices[1]+1):
		varday = [hour[var] for hour in data[ind]]
		varday = removeMissing(varday)
		varday = [float(value) for value in varday]
		if stat == 'mean':
			theStat.append(numpy.mean(varday))
		elif stat == 'max':
			theStat.append(max(varday))
		elif stat == 'min':
			theStat.append(min(varday))
	return theStat

def plotDailyStat(date, data, var, start_date, end_date, stat='mean', title=''):
	import matplotlib.pyplot as plt
	import matplotlib.dates as mdates
	years = mdates.YearLocator()   # every year
	months = mdates.MonthLocator()  # every month
	daysLocator = mdates.DayLocator()  # every day
	theFormat = mdates.DateFormatter('%Y-%b')
	# find indices of start and end dates
	indices = [i for i,x in enumerate(date) \
			if x.isoformat() == start_date \
			or x.isoformat() == end_date]
	if len(indices) < 2:
		print "dates not in range"
		return -1
	else:
		print "index range plotted: ", indices
	# for each day, process variable and compute statistic
	theStat = computeStatistic(var,stat,data,indices)
	# get requested dates 
	datelist = [day for day in date[indices[0]:indices[1]+1]]
	# make plot
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.grid(True)
	# ax.plot(range(len(varlist)),varlist)
	ax.plot(datelist,theStat)
	ax.xaxis.set_major_locator(months)
	ax.xaxis.set_major_formatter(theFormat)
	ax.xaxis.set_minor_locator(daysLocator)
	plt.ylabel('Daily ' + stat + ' ' + var)
	plt.title(title)
	fig.autofmt_xdate()
	plt.show()

#------------- comparison plot of a daily statistic over a time interval
def compareDailyStat(date, dataList, var, start_date, end_date, stat='mean', title=''):
	import matplotlib.pyplot as plt
	import matplotlib.dates as mdates
	import matplotlib
	matplotlib.rcParams['axes.color_cycle'] = ['r', 'k', 'c']
	years = mdates.YearLocator()   # every year
	months = mdates.MonthLocator()  # every month
	daysLocator = mdates.DayLocator()  # every day
	theFormat = mdates.DateFormatter('%Y-%b')
	# find indices of start and end dates
	indices = [i for i,x in enumerate(date) \
			if x.isoformat() == start_date \
			or x.isoformat() == end_date]
	if len(indices) < 2:
		print "dates not in range"
		return -1
	else:
		print "index range plotted: ", indices
	# for each day, process variable and compute statistic
	theStat = []
	for data in dataList:
		theStat.append(computeStatistic(var,stat,data,indices))
	# get requested dates 
	datelist = [day for day in date[indices[0]:indices[1]+1]]
	# make plot
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.grid(True)
	# ax.plot(range(len(varlist)),varlist)
	for aStat in theStat:
		ax.plot(datelist,aStat)
	ax.xaxis.set_major_locator(months)
	ax.xaxis.set_major_formatter(theFormat)
	ax.xaxis.set_minor_locator(daysLocator)
	plt.ylabel('Daily ' + stat + ' ' + var)
	plt.title(title)
	fig.autofmt_xdate()
	plt.show()



