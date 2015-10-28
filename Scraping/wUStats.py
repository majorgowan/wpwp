###############################################################
###################### COLLECT DAILY STATS ####################
###############################################################
#
def collectAllStats():
     import wUnderground as wU
     stations = getStationList()
     stations = ['CYYZ', 'CYUL']
     for station in stations:
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

          print('date, TempMean, TempMin, TempMinTime, ' \
                + 'TempMax, TempMaxTime, TotalPrecip, VisibilityMean, ' \
                + 'PressMean, PressMin, PressMinTime, ' \
                + 'PressMax, PressMaxTime, HumidityMean, ' \
                + 'WindMaxSpd, WindMaxDir, WindMaxTime, ' \
                + 'WindMeanX, WindMeanY')
          for ii in [0, 1, 2]:
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
               print(dataString)


###############################################################
###################### GET ALL STATIONS #######################
###############################################################
#
def getStationList():
     import glob
     stations = []
     for infile in glob.glob('JSON_DATA/*'):
         stations.append(infile.split('\\')[1])
     return stations

###############################################################
###################### DERIVED STATS ##########################
###############################################################
#
def isMissing(valString):
     if (valString in ['N/A', '-9999', '']):
          return True
     else:
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
                         math.cos(radperdeg*float(hour['WindDirDegrees']))
                    ys = - float(hour['Wind SpeedKm/h']) * \
                         math.sin(radperdeg*float(hour['WindDirDegrees']))
                    hour[u'xSpeed'] = unicode('%.2f' % xs)
                    hour[u'ySpeed'] = unicode('%.2f' % ys)

#
def dailyMean(data, variable):
     dm = []
     secperday = 24*60*60
     # loop over days
     for day in data:
          time = []
          val = []
          # isolate time of day and variable
          for hour in day:
               todString = hour['DateUTC'].split(' ')[1]
               tod = todString.split(':')
               seconds = 3600*int(tod[0]) \
                         + 60*int(tod[1]) + int(tod[2])
               value = hour[variable]
               # if not missing value
               if not isMissing(value):
                    time.append(seconds)
                    try:
                        val.append(float(value))
                    except:
                        print(day[0]['DateUTC'] + ' ' + str(value))
                        return -1
          # compute mean using trapezoid method
          onemean = 0.0
          for ii in range(len(time)-1):
               onemean += 0.5*((time[ii+1]-time[ii]) % secperday) \
                                        * (val[ii]+val[ii+1])
          onemean /= ((time[-1] - time[0]) % secperday)
          dm.append(onemean)
     return dm
#

def dailySum(data, variable):
     ds = []
     for day in data:
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
          maxtime = day[val.index(maxval)]['DateUTC'].split(' ')[1]
          dm.append(maxval)
          dmpos.append(maxtime)
     return dm, dmpos
#

def dailyMaxWind(data):
     dmspd = []
     dmdir = []
     dmtime = []
     # loop over days
     for day in data:
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
          maxdir = int(day[val.index(maxval)]['WindDirDegrees'])
          maxtime = day[val.index(maxval)]['DateUTC'].split(' ')[1]
          dmspd.append(maxval)
          dmdir.append(maxdir)
          dmtime.append(maxtime)
     return dmspd, dmdir, dmtime

###############################################################
###################### INTERACTIVE EXAMPLE ####################
###############################################################
#
'''
'''

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

