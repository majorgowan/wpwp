################################################################
################## COMPUTE DIRECTIONAL DERIVATIVE ##############
#################### OF A VARIABLE IN DIRECTION ################
################ FROM SOURCE STATION TO TARGET STATION #########
################################################################
#
###############################################################
################## HELPER FUNCTIONS ###########################
###############################################################
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
     
def unitVector(lon, lat):
     # compute unit vector in direction from station1 to station2
     # returns 2-component numpy array
     import numpy as np
     lonlat1 = np.array([lon[0], lat[0]])
     lonlat2 = np.array([lon[1], lat[1]])
     diff = lonlat2 - lonlat1
     return diff / np.linalg.norm(diff)

###############################################################
################## DIRECTIONAL DERIVATIVE #####################
###############################################################
#
def dDeriv(station1, station2, variable, startDate, endDate):
     # compute directional derivative using
     # (unitVector . windX2, windY2) (var1 - var2)
     import numpy as np
     # load longitude and latitude of both stations
     lon, lat = getStationLonLat([station1, station2])
     # compute unit vector from station2 to station1
     uVec = unitVector(lon, lat)
     # print("unit vector: " + str(uVec))
     # get mean wind vector at station2:
     windX2 = loadDailyVariableRange(station2, startDate, endDate, \
                        'WindMeanX', castFloat=True)
     windY2 = loadDailyVariableRange(station2, startDate, endDate, \
                        'WindMeanY', castFloat=True)
     # get variable at station1 and station2
     var1 = loadDailyVariableRange(station1, startDate, endDate, \
                        variable, castFloat=True)
     var2 = loadDailyVariableRange(station2, startDate, endDate, \
                        variable, castFloat=True)
     # construct wind vectors (N x 2 array)
     windVec = np.vstack((windX2, windY2))
     # project wind vector onto unit vector
     proj = np.dot(uVec, windVec)
     dD = (np.array(var1) - np.array(var2)) * proj
     return dD, uVec


