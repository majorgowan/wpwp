###############################################################
###################### GET ALL STATIONS #######################
###############################################################
#
def getStationList():
     import glob
     stations = []
     for infile in sorted(glob.glob('JSON_DATA/*')):
         stations.append(infile.split('\\')[1])
     return stations

#
def getStationLonLat(stations):
     # data from http://ourairports.com/data/
     # identifier in column 1 (0-based), lat-lon in columns 4,5
     lon = []
     lat = []
     for station in stations:
          with open('AIRPORT_DATA/airports.csv') as airportfile:
               for nline in airportfile:
                    nlist = nline.split(',')
                    if station in nlist[1]:
                        lon.append(float(nlist[5]))
                        lat.append(float(nlist[4]))
                        break
     return lon, lat               
     
###############################################################
#################### LOAD VARIABLE FROM CSV ###################
###############################################################
#
def loadDailyVariable(stations, outdate, variable):
     vals = []
     for station in stations:
          with open('CSV_DATA/' + station + '.csv','r') as infile:
               header = infile.readline().strip().split(', ')
               datepos = header.index('date')
               varpos = header.index(variable)
               for nline in infile:
                    nlist = nline.strip().split(', ')
                    nday = nlist[datepos]
                    if nday == outdate:
                         vals.append(float(nlist[varpos]))
                         break
     return vals          

#
def loadDailyVariableRange(station, startDate, endDate, \
                           variable, castFloat=False):
     # generate a list of values for a specified variable from
     # a specified station over a specified range of dates
     #
     # check if variable is a derived variable or a stored variable
     import wUDerived as Deriv
     reload(Deriv)
     # if derived, will be a method in wUDerived module
     if hasattr(Deriv, variable):
          methodToCall = getattr(Deriv, variable)
          return methodToCall(station, startDate, endDate)
     # else should be stored in CSV file
     vals = []
     with open('CSV_DATA/' + station + '.csv','r') as infile:
          header = infile.readline().strip().split(', ')
          datepos = header.index('date')
          varpos = header.index(variable)
          recording = False
          for nline in infile:
               nlist = nline.strip().split(', ')
               nday = nlist[datepos]
               if nday == startDate:
                    recording = True
               if recording:
                    if castFloat:
                         vals.append(float(nlist[varpos]))
                    else:
                         vals.append(nlist[varpos])
               if nday == endDate:
                    recording = False
                    break
     return vals

###############################################################
#################### MISCELLANEOUS ############################
###############################################################
#
def smooth(data, window=3):
     # a simple running mean "boxcar filter"; window is an odd integer
     import numpy as np
     shift = window / 2  # integer division
     last = len(data)-1
     newdata = []
     for ii in range(len(data)):
         start = max(0,ii-shift)
         end = min(last,ii+shift)
         val = np.mean(data[start:(end+1)])
         newdata.append(val) 
     return newdata

def dateList(startDate, endDate):
     # generate list of datetime objects for a range of dates
     # (mostly for plotting purposes)
     import datetime
     day0 = datetime.datetime.strptime(startDate,"%Y-%m-%d")
     dayN = datetime.datetime.strptime(endDate,"%Y-%m-%d")
     N = (dayN-day0).days
     date_list = [day0 + datetime.timedelta(days = n) for n in range(0,N+1)]
     return date_list

