import requests
import datetime

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
     if not os.path.exists('JSON_DATA/' + station):
         os.mkdir('JSON_DATA/' + station)
     # create filename
     filename = 'JSON_DATA/' + station + '/'
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
     filename = 'JSON_DATA/' \
                + station + '/' + station + '_' + str(year) + '_' \
                + str('%02d' % month) + '.json'
     with open(filename, 'r') as infile:
          # print(filename)
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
     for infile in sorted( \
            glob.glob(os.path.join('JSON_DATA\\' + station,'*.json')) ):
         station = infile.split('\\')[1]
         year = int(infile.split('\\')[2].split('_')[1])
         month = int(infile.split('\\')[2].split('_')[2].split('.')[0])
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
