###############################################################
################## HELPER FUNCTIONS ###########################
###############################################################
#
def loadDailyVariableRange(station, startDate, endDate, \
                           variable, castFloat=False):
     # generate a list of values for a specified variable from
     # a specified station over a specified range of dates
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

################################################################
################## DERIVED STATISTICS ##########################
################################################################
#
def dailyTempRange(station, startDate, endDate):
     import datetime
     # get daily range (positive if max occurs later than min)
     maximum = loadDailyVariableRange(station, startDate, endDate, \
                           'TempMax', castFloat=True)
     minimum = loadDailyVariableRange(station, startDate, endDate, \
                           'TempMin', castFloat=True)
     maxTime = loadDailyVariableRange(station, startDate, endDate, \
                           'TempMaxTime', castFloat=False)
     minTime = loadDailyVariableRange(station, startDate, endDate, \
                           'TempMinTime', castFloat=False)
     # positive if maximum occurs later than minimum
     plusminus = [2*int(datetime.datetime.strptime(maxTime[i],"%Y-%m-%d %H:%M:%S")
                      - datetime.datetime.strptime(minTime[i],"%Y-%m-%d %H:%M:%S") 
                          > datetime.timedelta(0)) - 1 \
                                    for i in range(len(maxTime))]
     # calculate return value                                        
     vals = [float(plusminus[i]*(maximum[i]-minimum[i])) \
                                    for i in range(len(plusminus))]
     return vals

#
def dailyPressRange(station, startDate, endDate):
     import datetime
     # get daily range (positive if max occurs later than min)
     maximum = loadDailyVariableRange(station, startDate, endDate, \
                           'PressMax', castFloat=True)
     minimum = loadDailyVariableRange(station, startDate, endDate, \
                           'PressMin', castFloat=True)
     maxTime = loadDailyVariableRange(station, startDate, endDate, \
                           'PressMaxTime', castFloat=False)
     minTime = loadDailyVariableRange(station, startDate, endDate, \
                           'PressMinTime', castFloat=False)
     # positive if maximum occurs later than minimum
     plusminus = [2*int(datetime.datetime.strptime(maxTime[i],"%Y-%m-%d %H:%M:%S")
                      - datetime.datetime.strptime(minTime[i],"%Y-%m-%d %H:%M:%S") 
                          > datetime.timedelta(0)) - 1 \
                                    for i in range(len(maxTime))]
     # calculate return value
     vals = [float(plusminus[i]*(maximum[i]-minimum[i])) \
                                    for i in range(len(plusminus))]
     return vals

#
def isWesterly(station, startDate, endDate):
     # binary variable for max wind (0 = easterly, 1 = westerly)
     windDir = loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w > 180.0 and w < 360.0) for w in windDir]

#
def isEasterly(station, startDate, endDate):
     # binary variable for max wind (0 = easterly, 1 = westerly)
     windDir = loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w > 0.0 and w < 180.0) for w in windDir]

#
def isSoutherly(station, startDate, endDate):
     # binary variable for max wind (0 = northerly, 1 = southerly)
     windDir = loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w > 90.0 and w < 270.0) for w in windDir]
     
#
def isNortherly(station, startDate, endDate):
     # binary variable for max wind (0 = northerly, 1 = southerly)
     windDir = loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w > 270.0 or w < 90.0) for w in windDir]
     
#
def windQuadrant(station, startDate, endDate):
     # integer variable for quadrant of maximum wind
     windDir = loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w)/90 for w in windDir]

#
def isFoggy(station, startDate, endDate):
     # binary variable for fogginess (visibility < 5 km)
     visibility = loadDailyVariableRange(station, startDate, endDate, \
                           'VisibilityMean', castFloat=True)
     return [int(v < 5.0) for v in visibility]

#
def isNotFoggy(station, startDate, endDate):
     # binary variable for fogginess (visibility < 5 km)
     visibility = loadDailyVariableRange(station, startDate, endDate, \
                           'VisibilityMean', castFloat=True)
     return [int(v > 5.0) for v in visibility]

