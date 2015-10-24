import requests
import datetime
import numpy

###############################################################
###################### INTERACTIVE EXAMPLE ####################
###############################################################
#
'''
# In Python terminal session:
import wUnderground
# read data and save in tuple DDD
DDD = wUnderground.TorontoMontreal_Winter_2002_2003()
# prepare plots
PPP = wUnderground.PreparePlots(*DDD)
# draw example plots
wUnderground.DrawPlots(*PPP)
#
#------------------
# make a plot of difference in maximum Temp between Tor and Mtl 
# in December 2002 (by hand)
import matplotlib.pyplot as plt
from numpy import array
plotDate, plotTor, plotMtl = PPP
# find indices corresponding to desired date range
indices = [i for i,x in enumerate(plotDate) \
		if x.isoformat() == '2002-12-01' \
		or x.isoformat() == '2002-12-31']
Tmax_Tor = wUnderground.computeStatistic('TemperatureC','max',plotTor,indices)
Tmax_Mtl = wUnderground.computeStatistic('TemperatureC','max',plotMtl,indices)
december = plotDate[indices[0]:indices[1]+1]
# create figure
fig = plt.figure()
ax = fig.add_subplot(111)
ax.grid(True)
ax.fill_between(december,Tmax_Tor,Tmax_Mtl, \
          where=array(Tmax_Mtl)<=array(Tmax_Tor), \
		interpolate=True, facecolor='wheat')
ax.fill_between(december,Tmax_Tor,Tmax_Mtl, \
          where=array(Tmax_Mtl)>=array(Tmax_Tor), \
		interpolate=True, facecolor='salmon')
pt, = ax.plot(december,Tmax_Tor,color='r',label='Toronto')
pm, = ax.plot(december,Tmax_Mtl,color='b',label='Montreal')
fig.autofmt_xdate()
plt.title('Difference between daily max temp in Toronto and Montreal')
plt.ylabel('Daily max temperature (C)')
plt.legend(handles=[pt,pm])
plt.show()
'''
#
###############################################################
########################## JSON I/O ###########################
###############################################################
#
#--
# write to JSON files
def putJSON(dates, data, station, year, month):
     import json
     import os
     # check if station folder exists
     if not os.path.exists(station):
         os.mkdir(station)
     # create filename
     filename = station + '/'
     filename += station + '_' + str(year) + '_'
     filename += str('%02d' % month) 
     filename += '.json'
     # open file for writing (close automatically)
     with open(filename, 'w') as outfile:
          # extract month of data
          block = [data[i] for i in range(len(dates)) \
                 if dates[i].year==year and dates[i].month==month]
          # write block to file
          outfile.write(json.dumps(block,indent=2))
#
# read from JSON files
#--
def getJSON(station, year, month):
     import json
     # build filename
     filename = station + '/' + station + '_' + str(year) + '_' \
                + str('%02d' % month) + '.json'
     with open(filename, 'r') as infile:
          data = json.load(infile)
     # make list of dates
     dates = []
     for day in range(1,daysInMonth(year,month)+1):
         dates.append(datetime.date(year,month,day))
     return dates, data

#
# retrieve and store a year from a single station
#--
def retrieveStationYear(station, year):
     start = str(year) + '-01'
     end = str(year) + '-12'
     dates, data, fails = readInterval(station, start, end)
     print('Number of fails ' + str(len(fails)))
     # store as JSON in month-long blocks
     for month in range(1,13):
          putJSON(dates, data, station, year, month)
     
# read entire station folder
#--
def getJSONFolder(station):
     import glob
     import os
     dates = []
     data = []
     for infile in glob.glob(os.path.join(station,'*.json')):
         station = infile.split('_')[0].split('\\')[0]
         year = int(infile.split('_')[1])
         month = int(infile.split('_')[2].split('.')[0])
         dates0, data0 = getJSON(station,year,month)
         dates.extend(dates0)
         data.extend(data0)
     return dates, data
          
#
'''
e.g. load 8 years of Pittsburgh:
for year in range(2005,2013):
    wUnderground.retrieveStationYear('KPIT', year)
'''
#          
###############################################################
########################## PLOTTING ###########################
###############################################################
#
#--
def DrawPlots(plotDate, plotTor, plotMtl):
	# load matplotlib.pyplot
	import matplotlib.pyplot as plt
	# -- plot ranges of SLP and TempC for Toronto
	plotDailyRange(plotDate, plotTor, 'Sea Level PressurehPa', \
			'2002-12-21', '2003-03-20', \
			title='Toronto Winter 2002-2003', show=False)
	plotDailyRange(plotDate, plotTor, 'TemperatureC', \
			'2002-12-21', '2003-03-20', \
			title='Toronto Winter 2002-2003', show=False)
	# compare daily minimum temperature from Toronto and Montreal
	compareDailyStat(plotDate, [plotTor, plotMtl], 'TemperatureC', \
			'2002-12-21', '2003-03-20', \
			leg = ['Toronto', 'Montreal'], \
			stat='min', \
			title='Winter 2002-2003', \
			show=False)
	# repeat for max wind speed
	compareDailyStat(plotDate, [plotTor, plotMtl], 'Wind SpeedKm/h', \
			'2002-12-21', '2003-03-20', \
			leg = ['Toronto', 'Montreal'], \
			stat='max', \
			title='Winter 2002-2003', \
			show=False)
	# repeat for min humidity
	compareDailyStat(plotDate, [plotTor, plotMtl], 'Humidity', \
			'2002-12-21', '2003-03-20', \
			leg = ['Toronto', 'Montreal'], \
			stat='min', \
			title='Winter 2002-2003', \
			show=False)
	plt.show()
#--
def PreparePlots(dates, tor, tor_fails, mtl, mtl_fails):
	# -- remove days missing from one or the other
	fail_indices = [fl[0] for fl in tor_fails] \
			and [fl[0] for fl in mtl_fails]
	plotDate = []; plotTor = []; plotMtl = []
	# -- prepare clean data sets
	for iday in range(len(dates)):
		if iday not in fail_indices:
			plotDate.append(dates[iday])
			plotTor.append(tor[iday])
			plotMtl.append(mtl[iday])
	# make plots
	return plotDate, plotTor, plotMtl
#--
def TorontoMontreal_Winter_2002_2003():
	# accumulate data from weather underground
	dates, tor, tor_fails = readInterval('CYYZ','2002-12','2003-03')
	dates, mtl, mtl_fails = readInterval('CYUL','2002-12','2003-03')
	# prepare data for plots (and plot)
	PreparePlots(dates, tor, tor_fails, mtl, mtl_fails)
	# return data
	return dates, tor, tor_fails, mtl, mtl_fails

###############################################################
###################### RETRIEVE WUNDERGROUND PAGE #############
###############################################################
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
def readStationCoord(data):
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
	pass

#------------- get number of days in given month (includes leap year calculator)
def daysInMonth(year, month):
	dim = [31, 28, 31, 30, 31, 30, 31, 31,\
		30, 31, 30, 31]
	if month==2:
		# check if leap year
		if year%4 == 0 and (year%100 != 0 or year%400 == 0):
			return 29
	return dim[month-1]

#------------- convert an hour of data from raw list to a dictionary
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

###############################################################
###################### MAIN DATA RETRIEVAL ROUTINE ############
###############################################################
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
# --
# Frankfurt:     EDDF

#------------- read a block of months from a single station
def readInterval(stationCode, start, end):
	# stationCode : string (e.g. 'CYYZ' for Toronto Pearson)
	# start, end : strings in form "YYYY-MM"
	date = []
	data = []
	# keep track of read failures (usu. page with headings and no data)
	failures = []
	startYear = int(start[:4]);  endYear = int(end[:4])
	startMonth = int(start[5:]); endMonth = int(end[5:])
	# loop over years
	for year in range(startYear,endYear+1):
		# compute start and end month for this year
		if year == startYear: 
			sMonth = startMonth
		else:
			sMonth = 1
		if year == endYear: 
			eMonth = endMonth
		else:
			eMonth = 12
		# loop over months in year
		for month in range(sMonth,eMonth+1):
			# loop over days in month
			for day in range(1,daysInMonth(year,month)+1):
				stationDay = readStationDay(stationCode, \
						year, month, day)
				oneDay, success = readDay(stationDay)
				# if read failure, save the date and index
				if success == -1: 
					print "retrieval error: ", \
						year, month, day
					failures.append((len(data), \
						stationCode, year, month, day))
				# append data to lists
				date.append(datetime.date(year,month,day))
				data.append(oneDay)
	print "\n\nThere were", len(failures), "failures!! . . .\n\n\n"
	# go back and retry failures (up to maxIter times)
	ii = 0
	maxIter = 5
	while len(failures) > 0 and ii < maxIter:
		ii += 1
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
	# any remaining failures probably genuinely missing data
	return date, data, failures

###############################################################
###################### FILE I/O ###############################
###############################################################
#------------- write data to file
def writeToFile(station, data):
	pass

#------------- read data from file
def readFromFile(fileName):
	pass

###############################################################
###################### DATA CLEANING ##########################
###############################################################
#------------- replace missing values in a list with averages
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


###############################################################
###################### PLOTTING ROUTINES ######################
###############################################################
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

def plotData(date, data, var, start_date, end_date, title='', show=True):
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
	if show: plt.show()

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

def plotDailyStat(date, data, var, start_date, end_date, \
		stat='mean', title='', show=True):
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
	if show: plt.show()

#------------- min, mean, max plot of a variable over a time interval
def plotDailyRange(date, data, var, start_date, end_date, title='', show=True):
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
	if show: plt.show()


#------------- comparison plot of a daily statistic over a time interval
def compareDailyStat(date, dataList, var, start_date, end_date, leg = [], \
		stat='mean', title='', show=True):
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
	if len(leg) > 0: ax.legend(leg)
	ax.xaxis.set_major_locator(months)
	ax.xaxis.set_major_formatter(theFormat)
	ax.xaxis.set_minor_locator(daysLocator)
	plt.ylabel('Daily ' + stat + ' ' + var)
	plt.title(title)
	fig.autofmt_xdate()
	if show: plt.show()



