import wUnderground as wu
import datetime
import numpy

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
     dmpos = []
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
          dmpos.append(maxtime)
     return dmspd, dmdir, dmpos

def dailyMeanWind(data):
     import math
     secperday = 24*60*60
     radperdeg = math.pi / 180
     dmxspd = []
     dmyspd = []
     # loop over days
     for day in data:
          time = []
          valspd = []
          valdir = []
          # isolate time of day and variable
          for hour in day:
               todString = hour['DateUTC'].split(' ')[1]
               tod = todString.split(':')
               seconds = 3600*int(tod[0]) \
                         + 60*int(tod[1]) + int(tod[2])
               value = hour['Wind SpeedKm/h']
               dirn = hour['WindDirDegrees']
               if value == 'Calm':
                   value = '0.0'
                   dirn = '0.0'
               # if not missing value
               if not isMissing(value):
                    time.append(seconds)
                    try:
                        valspd.append(float(value))
                        valdir.append(float(dirn)*radperdeg)
                    except:
                        print(day[0]['DateUTC'] + ' ' + str(value) + ' ' + str(dirn))
                        return -1
          # compute mean using trapezoid method
          xmean = 0.0
          ymean = 0.0
          for ii in range(len(time)-1):
               dt = (time[ii+1]-time[ii]) % secperday
               xx = 0.5*(valspd[ii]*math.cos(valdir[ii] \
                       + valspd[ii+1]*math.cos(valdir[ii+1])))
               yy = -0.5*(valspd[ii]*math.sin(valdir[ii] \
                       + valspd[ii+1]*math.sin(valdir[ii+1])))
               xmean += dt*xx
               ymean += dt*yy
          xmean /= ((time[-1] - time[0]) % secperday)
          ymean /= ((time[-1] - time[0]) % secperday)
          dmxspd.append(xmean)
          dmyspd.append(ymean)
     return dmxspd, dmyspd

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

