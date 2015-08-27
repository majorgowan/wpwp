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
			self.recording += 1

	def handle_endtag(self, tag):
		if tag=='td': 
			#print "Recording? " + `self.recording`
			#print "Encountered a end tag:", tag
			self.recording -= 1

	def handle_data(self, data):
		if self.recording:
			#print "Encountered some data:", data
			self.data.append(data)

def readStationDay(stationID, year, month, day):
	base = "http://climate.weather.gc.ca/climateData/hourlydata_e.html"
	base = base + "?timeframe=1&Prov=ON&StationID=51459"
	theUrl = base + "&StationID=" + `stationID` + \
			"&Year=" + `year` + \
			"&Month=" + `month` + "&Day=" + `day`
	page = requests.get(theUrl)
	#print page.text
	parser = MyHTMLParser()
	parser.feed(page.text)
	return parser

#def chunker(seq, size):
#	return (seq[pos:pos + size] \
#		for pos in xrange(0, len(seq), size))

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

def readHour(data):
	hour = data[0]
	temp = data[2]
	dewp = data[3]
	humid = data[4]
	winddir = data[5]
	windsp = data[6]
	visible = data[7]
	press = data[8]
	return {'hour': hour, 'temp': temp, \
		'dewp': dewp, 'humid': humid, \
		'winddir': winddir, 'windsp': windsp, \
		'visibility': visible, \
		'pressure': press}

def readDay(data):
	# find indices of rows in data
	indices = [i-1 for i, \
		x in enumerate(data) \
		if x == "Legend Double Dagger"]
	hours = []
	for hour in indices:
		hours.append(readHour(data[hour:]))
	return hours

def readToronto():
	counter = 0
	days = []
	data = []
	year = 2014
	stationID = 51459
	for month in range(12):
		for day in range(30):
			stationDay = readStationDay(stationID, \
					year, month, day)
			counter += 1
			days.append(counter)
			data.append(readDay(stationDay.data))
	return days, data






		
