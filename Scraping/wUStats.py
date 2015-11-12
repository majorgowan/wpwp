###############################################################
###################### COLLECT DAILY STATS ####################
###############################################################
#
def collectAllStats():
     import wUnderground as wU
     import os
     if not os.path.exists('CSV_DATA'):
         os.mkdir('CSV_DATA')
     #stations = ['CYYZ', 'CYUL']
     stations = getStationList()
     for station in stations:
          print('Processing ' + station)
          # open file for csv output
          outfile = open('CSV_DATA/' + station + '.csv','w')
          # calculate summary statistics
          dates, data = wU.getJSONFolder(station)
          TempMean = dailyMean(data,'TemperatureC')
          TempMin, TempMinTime = dailyMax(data,'TemperatureC',-1)
          TempMax, TempMaxTime = dailyMax(data,'TemperatureC',1)
          TotalPrecip = dailySum(data,'Precipitationmm')
          VisibilityMean = dailyMean(data,'VisibilityKm')
          PressMean = dailyMean(data, 'Sea Level PressurehPa')
          PressMin, PressMinTime = dailyMax(data,'Sea Level PressurehPa',-1)
          PressMax, PressMaxTime = dailyMax(data,'Sea Level PressurehPa',1)         
          HumidityMean = dailyMean(data,'Humidity')
          WindMaxSpd, WindMaxDir, WindMaxTime = dailyMaxWind(data)
          
          addWindVectors(data)
          WindMeanX = dailyMean(data,'xSpeed')
          WindMeanY = dailyMean(data,'ySpeed')

          headString = 'date, TempMean, TempMin, TempMinTime, ' \
                + 'TempMax, TempMaxTime, TotalPrecip, VisibilityMean, ' \
                + 'PressMean, PressMin, PressMinTime, ' \
                + 'PressMax, PressMaxTime, HumidityMean, ' \
                + 'WindMaxSpd, WindMaxDir, WindMaxTime, ' \
                + 'WindMeanX, WindMeanY'
          # print(headString)
          outfile.write(headString + '\n')
          for ii in range(len(dates)):
               dataString = dates[ii].isoformat() + ', '
               dataString += unicode('%.2f' % TempMean[ii]) + ', '
               dataString += unicode(TempMin[ii]) + ', '
               dataString += unicode(TempMinTime[ii]) + ', '
               dataString += unicode(TempMax[ii]) + ', '
               dataString += unicode(TempMaxTime[ii]) + ', '
               dataString += unicode(TotalPrecip[ii]) + ', '
               dataString += unicode('%.1f' % VisibilityMean[ii]) + ', '
               dataString += unicode('%.0f' % PressMean[ii]) + ', '
               dataString += unicode(PressMin[ii]) + ', '
               dataString += unicode(PressMinTime[ii]) + ', '
               dataString += unicode(PressMax[ii]) + ', '
               dataString += unicode(PressMaxTime[ii]) + ', '
               dataString += unicode('%.0f' % HumidityMean[ii]) + ', '
               dataString += unicode(WindMaxSpd[ii]) + ', '
               dataString += unicode(WindMaxDir[ii]) + ', '
               dataString += unicode(WindMaxTime[ii]) + ', '
               dataString += unicode('%.2f' % WindMeanX[ii]) + ', '
               dataString += unicode('%.2f' % WindMeanY[ii])
               # write daily summary to csv file
               outfile.write(dataString + '\n')
               # print(dataString)
          outfile.close()
          

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

###############################################################
###################### AGGREGATE STATS ########################
###############################################################
#
def isMissing(valString):
     if (valString in ['N/A', '-9999', '-9999.0', '']):
          return True
     else:
          # a few entries are very large numbers (corrupted no doubt)
          try:
               if abs(float(valString)) > 1.e5: 
                    return True
          except:
               pass
     # otherwise consider *not* missing
     return False

#
def addWindVectors(data):
     import math
     radperdeg = math.pi/180.0
     for day in data:
          for hour in day:
               if isMissing(hour['Wind SpeedKm/h']) or \
                  isMissing(hour['WindDirDegrees']):
                    hour[u'xSpeed'] = u'N/A'
                    hour[u'ySpeed'] = u'N/A'
               elif hour['Wind SpeedKm/h'] == 'Calm':
                    hour[u'xSpeed'] = u'0.0'
                    hour[u'ySpeed'] = u'0.0'
               else:
                    xs = - float(hour['Wind SpeedKm/h']) * \
                         math.sin(radperdeg*float(hour['WindDirDegrees']))
                    ys = - float(hour['Wind SpeedKm/h']) * \
                         math.cos(radperdeg*float(hour['WindDirDegrees']))
                    hour[u'xSpeed'] = unicode('%.2f' % xs)
                    hour[u'ySpeed'] = unicode('%.2f' % ys)

#
def toSecondsValues(utc, y):
     # convert pairs of (UTC, value) to 
     # (seconds since first value, value) removing missing values
     import datetime
     utcdatetime = [datetime.datetime.strptime(uu,"%Y-%m-%d %H:%M:%S") \
                                                      for uu in utc]
     time = []
     val = []
     for ii in range(len(utc)):
          if not isMissing(y[ii]):
               reftime = utcdatetime[ii]
               start = ii
               break
     for ii in range(start,len(utc)):
          if not isMissing(y[ii]):
               time.append(float((utcdatetime[ii]-reftime).total_seconds()))
               val.append(float(y[ii]))
     return time, val

def trapezoid(utc, y):
     import numpy
     # do a time integral of y over UTC time using trapezoid method
     # neglecting missing values
     time, val = toSecondsValues(utc, y)
     # print(zip(time,val))
     dt = [time[i+1]-time[i] for i in range(len(val)-1)]
     # print(zip(val,dt))
     integral = 0.0
     for ii in range(len(val)-1):
          integral += 0.5*dt[ii]*(val[ii] + val[ii+1])
     interval = numpy.sum(dt)
     return interval, integral

def rectangle(utc, y):
     import numpy
     secperday = float(24*60*60)
     # do a time integral of y over UTC time using forward rectangle method
     # neglecting missing values
     time, val = toSecondsValues(utc, y)
     # print(zip(time,val))
     # append secperday to beginning and end of time list:
     time = time + [secperday]
     dt = [time[i+1]-time[i] for i in range(len(val))]
     # print(zip(val,dt))
     integral = 0.0
     for ii in range(len(val)):
          integral += dt[ii]*val[ii]
     interval = numpy.sum(dt)
     return interval, integral
     
#
def dailyMean(data, variable, method='rectangle'):
     dm = []
     # loop over days
     for index, day in enumerate(data):
          # check if all missing
          allMissing = True
          for hour in day:
               value = hour[variable]
               if not isMissing(value):
                    allMissing = False
          if allMissing:
               dm.append(u'N/A')
          else:
               times = []
               values = []
               if method == 'trapezoid':
                    for hour in day:
                         times.append(hour['DateUTC'])
                         values.append(hour[variable])
                    # append first value of next day (if available)
                    if index < len(data)-1:
                         if not isMissing(data[index+1][0][variable]):
                              times.append(data[index+1][0]['DateUTC'])
                              values.append(data[index+1][0][variable])
                    interval, integral = trapezoid(times, values)
               elif method == 'rectangle':
                    for hour in day:
                         times.append(hour['DateUTC'])
                         values.append(hour[variable])
                    interval, integral = rectangle(times, values)
               dm.append(integral/interval)
     return dm
#

def dailySum(data, variable):
     ds = []
     for day in data:
          # check if all missing
          allMissing = True
          for hour in day:
               value = hour[variable]
               if not isMissing(value):
                    allMissing = False
          if allMissing:
               ds.append(u'N/A')
          else:
               # otherwise
               total = 0.0
               # isolate time of day and variable
               for hour in day:
                    value = hour[variable]    
                    if not isMissing(value):
                         total += float(value)
               ds.append(total)
     return ds
#

def dailyMax(data, variable, minmax=1):
     dm = []
     dmpos = []
     # loop over days
     for day in data:
          # check if all missing
          allMissing = True
          for hour in day:
               value = hour[variable]
               if not isMissing(value):
                    allMissing = False
          if allMissing:
               dm.append(u'N/A')
               dmpos.append(u'N/A')
          else:
               val = []
               # isolate time of day and variable
               for hour in day:
                    value = hour[variable]
                    # if not missing value
                    if not isMissing(value):
                         try:
                             val.append(float(value))
                         except:
                             print(day[0]['DateUTC'] + ' ' + str(value))
                             return -1
               # compute max or min
               if minmax == 1:
                    maxval = max(val)
               elif minmax == -1:
                    maxval = min(val)
               maxtime = day[val.index(maxval)]['DateUTC']
               dm.append(maxval)
               dmpos.append(maxtime)
     return dm, dmpos
#

# get the nearest non-missing value 
# (useful if wind direction missing for time of maximum wind)
def nearestNonMissing(day, variable, index):
     if not isMissing(day[index][variable]):
          return day[index][variable]
     else:
          print('Missing ' + variable + ' at index ' + str(index) \
                  + ' on UTC date ' + day[index]['DateUTC'])
          for ii in range(1,len(day)):
               if index-ii >= 0:
                    before = day[index-ii][variable]
               else:
                    before = 'N/A'
               if index+ii < len(day):
                    after = day[index+ii][variable]
               else:
                    after = 'N/A'
               if not isMissing(before):
                    return before
               elif not isMissing(after):
                    return after
     return u'N/A'

def dailyMaxWind(data):
     dmspd = []
     dmdir = []
     dmtime = []
     # loop over days
     for day in data:
          # check if all missing
          allMissing = True
          for hour in day:
               value = hour['Wind SpeedKm/h']
               if not isMissing(value):
                    allMissing = False
          if allMissing:
               dmspd.append(u'N/A')
               dmdir.append(u'N/A')
               dmtime.append(u'N/A')
          else:
               val = []
               # isolate time of day and variable
               for hour in day:
                    value = hour['Wind SpeedKm/h']
                    if value == 'Calm':
                        value = '0.0'
                    # if not missing value
                    if not isMissing(value):
                         try:
                             val.append(float(value))
                         except:
                             print(day[0]['DateUTC'] + ' ' + str(value))
                             return -1
               # compute max or min
               maxval = max(val)
               maxdir = nearestNonMissing(day,'WindDirDegrees',val.index(maxval))
               maxtime = day[val.index(maxval)]['DateUTC']
               dmspd.append(maxval)
               dmdir.append(maxdir)
               dmtime.append(maxtime)
     return dmspd, dmdir, dmtime

