import requests
from lxml import html
from HTMLParser import HTMLParser

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

def readStationCoord(data):
	# take table data list and extract station info
	# latitude:
	degrees = float(data[0])
	minutes = float(data[1])
	seconds = float(data[3])
	if data[5] == 'N':
		theSign = 1
	else:
		theSign = -1
	latitude = degrees + minutes/60 + seconds/3600
	# longitude:
	degrees = float(data[6])
	minutes = float(data[7])
	seconds = float(data[9])
	if data[11] == 'W':
		degrees = 360 - degrees
	longitude = degrees + minutes/60 + seconds/3600
	# elevation
	elevation = float(data[12])
	return {'long': round(longitude,3), \
		'lat': round(latitude,3), \
		'alt': round(elevation,3), \
		'symbol': data[16]
		}

def daysInMonth(year, month):
	dim = [31, 28, 31, 30, 31, 30, 31, 31,\
		30, 31, 30, 31]
	if month==2:
		# check if leap year
		if year%4 == 0 and (year%100 != 0 or year%400 == 0):
			return 29
	return dim[month-1]

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

def readToronto():
	date = []
	data = []
	year = 2014
	stationID = 51459
	for month in range(1,13):
		for day in range(1,daysInMonth(year,month)+1):
			stationDay = readStationDay(stationID, \
					year, month, day)
			date.append("%d-%02d-%02d" % (year,month,day))
			data.append(readDay(stationDay.data))
	return date, data

		
