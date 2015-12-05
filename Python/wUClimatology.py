###############################################################
################## BUILD CLIMATOLOGY FOR FEATURES #############
###############################################################
#
def makeClimatologies(stations, startDate, endDate, \
                      features, smoothWindow):
     # build climatology for set of features
     import wUUtils as Util
     import numpy as np

     # choose a leap year
     leap_year = Util.dateList('2008-01-01','2008-12-31')
     date_list = Util.dateList(startDate,endDate)

     climatologies=[]

     featureData = []
     for feature in features:
          fd = Util.loadDailyVariableSetRange(stations,startDate,endDate,[feature])
          featureData.append(fd)

     for fd in featureData:
          climatology = []
          for day_of_month in leap_year:
               # average of variable on this calendar day for all years
               this_day = np.mean([stationData[i] for i in range(len(date_list)) \
                                                  for stationData in fd \
                                                  if  date_list[i].month==day_of_month.month \
                                                  and date_list[i].day==day_of_month.day])
               climatology.append(this_day)
          # smooth
          climatology = Util.smooth(climatology,smoothWindow)     
          climatologies.append(climatology)
     return climatologies

#
def subtractClimatology(data, date_list, climatology):
     # subtract the climatology from the data
     import wUUtils as Util
     import numpy as np
     import datetime

     # choose a leap year
     leap_year = Util.dateList('2008-01-01','2008-12-31')

     pert = []
     for i,val in enumerate(data):
          doly = datetime.date(2008,date_list[i].month,date_list[i].day)
          ldoy = (doly-leap_year[0]).days
          pert.append(val-climatology[ldoy])
     return pert

#
def addClimatology(pert, date_list, climatology):
     # add the climatology to a perturbation to recover the full
     import wUUtils as Util
     import numpy as np
     import datetime

     # choose a leap year
     leap_year = Util.dateList('2008-01-01','2008-12-31')

     data = []
     for i,val in enumerate(pert):
          doly = datetime.date(2008,date_list[i].month,date_list[i].day)
          ldoy = (doly-leap_year[0]).days
          data.append(val+climatology[ldoy])
     return data
          
