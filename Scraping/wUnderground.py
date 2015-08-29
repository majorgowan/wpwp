import requests
import datetime
import numpy

#------------- use HTML parser to download web page with day of hourly data
def readStationDay(stationCode, year, month, day, echo=False):
	base = "http://www.wunderground.com/history/airport/"
	theUrl = base + stationCode + '/' + `year` + '/' + \
			`month` + '/' + `day` + '/' + \
			"DailyHistory.html?reqdb.magic=1&reqdb.wmo=99999&format=1"
	if echo: print "Retrieving " + theUrl
	page = requests.get(theUrl)
	return page.text

#------------- get station position (find from other source)
#def readStationCoord(data):
#	# latitude:
#	degrees = 
#	minutes = 
#	seconds = 
#	# longitude:
#	degrees = 
#	minutes = 
#	seconds =
#	# elevation
#	elevation = float(data[12])
#	return {'long': round(longitude,3), \
#		'lat': round(latitude,3), \
#		'alt': round(elevation,3), \
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
def readDay(data):
	hourlyData = []
	# strip trailing whitespace and split into lines (note html/text newline)
	lines = data.strip().strip('<br />').split('<br />\n')
	headings = lines[0].strip('<br />\n').split(',')
	for line in lines[1:]:
		hourlyData.append(dict(zip(headings, line.split(','))))
		if 'TemperatureC' not in hourlyData[-1].keys():
			return hourlyData, -1
	# print 'success', headings
	return hourlyData, 0

#------------- airport codes
# Halifax:       CYHZ
# Ottawa:        CYOW
# Montreal:      CYUL
# Toronto:       CYYZ
# Sudbury:       CYSB
# Thunder Bay:   CYQT
# Winnipeg:      CYWG
# Calgary:       CYYC
# Vancouver:     CYVR
# --
# Buffalo:       KBUF
# Chicago:       KORD
# Detroit: 	 KDTW
# Cleveland:	 KCLE
# Cincinnati:	 KCVG
# Pittsburgh:	 KPIT
# New York:	 KJFK
# Boston:	 KBOS
# Nashville:	 KBNA
# Memphis:	 KMEM
# Indianapolis:	 KIND
# Philadelphia:	 KPHL
# St. Louis:	 KSTL
# Milwaukee:	 KMKE
# Minneapolis:	 KMSP
# Charlotte:	 KCLT
# Washington:	 KIAD
# Des Moines:	 KDSM
# Kansas City:	 KMCI
# Dallas:	 KDFW
# Oklahoma City: KOKC


#------------- read a block of months from a single station
def readInterval(stationCode, start, end):
	# stationCode : string (e.g. 'CYYZ' for Toronto Pearson)
	# start, end : strings in form "YYYY-MM"
	date = []
	data = []
	failures = []
	startYear = int(start[:4]);  endYear = int(end[:4])
	startMonth = int(start[5:]); endMonth = int(end[5:])
	for year in range(startYear,endYear+1):
		if year == startYear: 
			sMonth = startMonth
		else:
			sMonth = 1
		if year == endYear: 
			eMonth = endMonth
		else:
			eMonth = 12
		for month in range(sMonth,eMonth+1):
			for day in range(1,daysInMonth(year,month)+1):
				stationDay = readStationDay(stationCode, \
						year, month, day)
				oneDay, success = readDay(stationDay)
				if success == -1: 
					print "retrieval error: ", \
						year, month, day
					failures.append((len(data), \
						stationCode, year, month, day))
				date.append(datetime.date(year,month,day))
				data.append(oneDay)
	# go back and redo failures!
	print "\n\nThere were", len(failures), "failures!! . . .\n\n\n"
	while len(failures) > 0:
		# copy failures from last pass
		lastFailures = failures[:]
		# keep track of failures from this pass
		failures = []
		for fail in lastFailures:
			print "retrying ", fail, ". . ."
			stationDay = readStationDay(*fail[1:])
			oneDay, success = readDay(stationDay)
			if success == -1: 
				print "failed again!"
				failures.append(fail)
			else: 
				print ". . . Gotcha!"
			data[fail[0]] = oneDay
		print "\n\n  now [only]", len(failures), "failures!! . . .\n\n\n"
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
	from datetime import datetime as dt
	# get values of variable and dates for desired range
	varlist = [hour[var] for day in data[indices[0]:indices[1]+1] for hour in day]
	datelist = [dt.strptime(hour['DateUTC'],'%Y-%m-%d %X') \
			for day in data[indices[0]:indices[1]+1] for hour in day]
	# replace -9999 values with empty string
	for i,value in enumerate(varlist):
		if varlist[i] == '-9999': varlist[i] = '' 
	# clean up data (convert to floats)
	varlist = removeMissing(varlist)
	# convert to floats
	varlist = [float(value) for value in varlist]
	return datelist, varlist

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
	# construct list of (date, var) pairs for the plot variable
	datelist, varlist = processVariable(var,data,indices)
	# make plot
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.grid(True)
	# ax.plot(range(len(varlist)),varlist)
	ax.plot(datelist,varlist)
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
		# replace -9999 values with empty string
		for i,value in enumerate(varday):
			if varday[i] == '-9999': varday[i] = '' 
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

#------------- min, mean, max plot of a variable over a time interval
def plotDailyRange(date, data, var, start_date, end_date, title=''):
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
	theMin = computeStatistic(var,'min',data,indices)
	theMax = computeStatistic(var,'max',data,indices)
	theMean = computeStatistic(var,'mean',data,indices)
	# get requested dates 
	datelist = [day for day in date[indices[0]:indices[1]+1]]
	# make plot
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.grid(True)
	# ax.plot(range(len(varlist)),varlist)
	ax.fill_between(datelist,theMin,theMax, facecolor='wheat')
	ax.plot(datelist,theMin,color='b')
	ax.plot(datelist,theMax,color='r')
	ax.plot(datelist,theMean,color='k')
	ax.xaxis.set_major_locator(months)
	ax.xaxis.set_major_formatter(theFormat)
	ax.xaxis.set_minor_locator(daysLocator)
	plt.ylabel('Daily range of ' + var)
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



