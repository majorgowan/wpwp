################################################################
################## DERIVED STATISTICS ##########################
################################################################
#
def dailyTempRange(station, startDate, endDate):
     import datetime
     import wUUtils as Util
     # get daily range (positive if max occurs later than min)
     maximum = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TempMax', castFloat=True)
     minimum = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TempMin', castFloat=True)
     maxTime = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TempMaxTime', castFloat=False)
     minTime = Util.loadDailyVariableRange(station, startDate, endDate, \
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
     import wUUtils as Util
     # get daily range (positive if max occurs later than min)
     maximum = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'PressMax', castFloat=True)
     minimum = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'PressMin', castFloat=True)
     maxTime = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'PressMaxTime', castFloat=False)
     minTime = Util.loadDailyVariableRange(station, startDate, endDate, \
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
     import wUUtils as Util
     windDir = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w > 180.0 and w < 360.0) for w in windDir]

#
def isEasterly(station, startDate, endDate):
     # binary variable for max wind (0 = easterly, 1 = westerly)
     import wUUtils as Util
     windDir = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w > 0.0 and w < 180.0) for w in windDir]

#
def isSoutherly(station, startDate, endDate):
     # binary variable for max wind (0 = northerly, 1 = southerly)
     import wUUtils as Util
     windDir = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w > 90.0 and w < 270.0) for w in windDir]
     
#
def isNortherly(station, startDate, endDate):
     # binary variable for max wind (0 = northerly, 1 = southerly)
     import wUUtils as Util
     windDir = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w > 270.0 or w < 90.0) for w in windDir]
     
#
def windQuadrant(station, startDate, endDate):
     # integer variable for quadrant of maximum wind
     import wUUtils as Util
     windDir = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxDir', castFloat=True)
     return [int(w)/90 for w in windDir]

#
def isFoggy(station, startDate, endDate):
     # binary variable for fogginess (visibility < 5 km)
     import wUUtils as Util
     visibility = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'VisibilityMean', castFloat=True)
     return [int(v < 5.0) for v in visibility]

#
def isNotFoggy(station, startDate, endDate):
     # binary variable for fogginess (visibility < 5 km)
     import wUUtils as Util
     visibility = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'VisibilityMean', castFloat=True)
     return [int(v > 5.0) for v in visibility]

################################################################
################## TIME-OF-DAY STATISTICS ######################
################################################################
#
def isMorningMinTemp(station, startDate, endDate):
     # binary variable for minimum temperature occurring before noon local time
     import datetime
     import wUUtils as Util
     mTime = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TempMinTime', castFloat=False)
     timeZone = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TimeZone', castFloat=True)
     # convert minTime to datetime
     mTime = [datetime.datetime.strptime(mm,"%Y-%m-%d %H:%M:%S") for mm in mTime]
     hours = [(mm.hour + mm.minute/60 + timeZone[i]) % 24 \
                                           for i,mm in enumerate(mTime)]
     isMorning = [int(hour < 12) for hour in hours]
     return(isMorning)

#
def isMorningMaxTemp(station, startDate, endDate):
     # binary variable for maximum temperature occurring before noon local time
     import datetime
     import wUUtils as Util
     mTime = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TempMaxTime', castFloat=False)
     timeZone = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TimeZone', castFloat=True)
     # convert maxTime to datetime
     mTime = [datetime.datetime.strptime(mm,"%Y-%m-%d %H:%M:%S") for mm in mTime]
     hours = [(mm.hour + mm.minute/60 + timeZone[i]) % 24 \
                                           for i,mm in enumerate(mTime)]
     isMorning = [int(hour < 12) for hour in hours]
     return(isMorning)

#
def isDaytimeMinPress(station, startDate, endDate):
     # binary variable for minimum pressure occurring before noon local time
     import datetime
     import wUUtils as Util
     mTime = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'PressMinTime', castFloat=False)
     timeZone = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TimeZone', castFloat=True)
     # convert minTime to datetime
     mTime = [datetime.datetime.strptime(mm,"%Y-%m-%d %H:%M:%S") for mm in mTime]
     hours = [(mm.hour + mm.minute/60 + timeZone[i]) % 24 \
                                           for i,mm in enumerate(mTime)]
     isDaytime = [int(hour > 8 and hour < 20) for hour in hours]
     return(isDaytime)

#
def isDaytimeMaxPress(station, startDate, endDate):
     # binary variable for maximum pressure occurring before noon local time
     import datetime
     import wUUtils as Util
     mTime = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'PressMaxTime', castFloat=False)
     timeZone = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TimeZone', castFloat=True)
     # convert maxTime to datetime
     mTime = [datetime.datetime.strptime(mm,"%Y-%m-%d %H:%M:%S") for mm in mTime]
     hours = [(mm.hour + mm.minute/60 + timeZone[i]) % 24 \
                                           for i,mm in enumerate(mTime)]
     isDaytime = [int(hour > 8 and hour < 20) for hour in hours]
     return(isDaytime)

#
def isMorningMaxWind(station, startDate, endDate):
     # binary variable for maximum wind speed occurring before noon local time
     import datetime
     import wUUtils as Util
     mTime = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'WindMaxTime', castFloat=False)
     timeZone = Util.loadDailyVariableRange(station, startDate, endDate, \
                           'TimeZone', castFloat=True)
     # convert maxTime to datetime
     mTime = [datetime.datetime.strptime(mm,"%Y-%m-%d %H:%M:%S") for mm in mTime]
     hours = [(mm.hour + mm.minute/60 + timeZone[i]) % 24 \
                                           for i,mm in enumerate(mTime)]
     isMorning = [int(hour < 12) for hour in hours]
     return(isMorning)





