
###############################################################
###################### DATA CLEANING ##########################
###############################################################
#------------- replace missing values in a list with averages
#------------- of nearest non-missing values
#-- get last (sign=-1) or next (sign=+1) valid float in data
def nextFloat(data, index, sign):
     try:
          f = float(data[index])
          return f
     except ValueError:
          if (sign == 1 and index == len(data)-1) \
                    or (sign == -1 and index == 0):
               return '9999'
          else:
               f = nextFloat(data,index+sign,sign)
               return f
#-- iterate over data and replace missing values
def removeMissing(data):
     import numpy
     ind = range(len(data))
     for ii in ind:
          # test if valid floating point value
          try:
               float(data[ii])
          except ValueError:
               last_float = nextFloat(data, ii, 1)
               next_float = nextFloat(data, ii, -1)
               data[ii] = str(numpy.mean([float(num) \
                    for num in [last_float, next_float] \
                    if num != '9999']))
     return data

###############################################################
###################### PLOTTING ROUTINES ######################
###############################################################
#------------- plot a variable over a time interval
#-- process variable
def processVariable(var,data,indices):
     from datetime import datetime as dt
     # get values of variable and dates for desired range
     varlist = [hour[var] for day in data[indices[0]:indices[1]+1] for hour in day]
     datelist = [dt.strptime(hour['DateUTC'],'%Y-%m-%d %X') \
               for day in data[indices[0]:indices[1]+1] for hour in day]
     # replace -9999 values with empty string
     for i,value in enumerate(varlist):
          if varlist[i] == '-9999': varlist[i] = '' 
     # clean up data (convert to floats)
     varlist = removeMissing(varlist)
     # convert to floats
     varlist = [float(value) for value in varlist]
     return datelist, varlist

def plotData(date, data, var, start_date, end_date, title='', show=True):
     import matplotlib.pyplot as plt
     import matplotlib.dates as mdates
     years = mdates.YearLocator()   # every year
     months = mdates.MonthLocator()  # every month
     daysLocator = mdates.DayLocator()  # every day
     theFormat = mdates.DateFormatter('%Y-%b')
     # find indices of start and end dates
     indices = [i for i,x in enumerate(date) \
               if x.isoformat() == start_date \
               or x.isoformat() == end_date]
     if len(indices) < 2:
          print "dates not in range"
          return -1
     else:
          print "index range plotted: ", indices
     # construct list of (date, var) pairs for the plot variable
     datelist, varlist = processVariable(var,data,indices)
     # make plot
     fig = plt.figure()
     ax = fig.add_subplot(111)
     ax.grid(True)
     # ax.plot(range(len(varlist)),varlist)
     ax.plot(datelist,varlist)
     ax.xaxis.set_major_locator(months)
     ax.xaxis.set_major_formatter(theFormat)
     ax.xaxis.set_minor_locator(daysLocator)
     plt.ylabel(var)
     plt.title(title)
     fig.autofmt_xdate()
     if show: plt.show()

#------------- plot a daily statistic over a time interval
#-- compute statistic
def computeStatistic(var,stat,data,indices):
     import numpy
     theStat = []
     for ind in range(indices[0],indices[1]+1):
          varday = [hour[var] for hour in data[ind]]
          # replace -9999 values with empty string
          for i,value in enumerate(varday):
               if varday[i] == '-9999': varday[i] = '' 
          varday = removeMissing(varday)
          varday = [float(value) for value in varday]
          if stat == 'mean':
               theStat.append(numpy.mean(varday))
          elif stat == 'max':
               theStat.append(max(varday))
          elif stat == 'min':
               theStat.append(min(varday))
     return theStat

def plotDailyStat(date, data, var, start_date, end_date, \
          stat='mean', title='', show=True):
     import matplotlib.pyplot as plt
     import matplotlib.dates as mdates
     years = mdates.YearLocator()   # every year
     months = mdates.MonthLocator()  # every month
     daysLocator = mdates.DayLocator()  # every day
     theFormat = mdates.DateFormatter('%Y-%b')
     # find indices of start and end dates
     indices = [i for i,x in enumerate(date) \
               if x.isoformat() == start_date \
               or x.isoformat() == end_date]
     if len(indices) < 2:
          print "dates not in range"
          return -1
     else:
          print "index range plotted: ", indices
     # for each day, process variable and compute statistic
     theStat = computeStatistic(var,stat,data,indices)
     # get requested dates 
     datelist = [day for day in date[indices[0]:indices[1]+1]]
     # make plot
     fig = plt.figure()
     ax = fig.add_subplot(111)
     ax.grid(True)
     # ax.plot(range(len(varlist)),varlist)
     ax.plot(datelist,theStat)
     ax.xaxis.set_major_locator(months)
     ax.xaxis.set_major_formatter(theFormat)
     ax.xaxis.set_minor_locator(daysLocator)
     plt.ylabel('Daily ' + stat + ' ' + var)
     plt.title(title)
     fig.autofmt_xdate()
     if show: plt.show()

#------------- min, mean, max plot of a variable over a time interval
def plotDailyRange(date, data, var, start_date, end_date, title='', show=True):
     import matplotlib.pyplot as plt
     import matplotlib.dates as mdates
     years = mdates.YearLocator()   # every year
     months = mdates.MonthLocator()  # every month
     daysLocator = mdates.DayLocator()  # every day
     theFormat = mdates.DateFormatter('%Y-%b')
     # find indices of start and end dates
     indices = [i for i,x in enumerate(date) \
               if x.isoformat() == start_date \
               or x.isoformat() == end_date]
     if len(indices) < 2:
          print "dates not in range"
          return -1
     else:
          print "index range plotted: ", indices
     # for each day, process variable and compute statistic
     theMin = computeStatistic(var,'min',data,indices)
     theMax = computeStatistic(var,'max',data,indices)
     theMean = computeStatistic(var,'mean',data,indices)
     # get requested dates 
     datelist = [day for day in date[indices[0]:indices[1]+1]]
     # make plot
     fig = plt.figure()
     ax = fig.add_subplot(111)
     ax.grid(True)
     # ax.plot(range(len(varlist)),varlist)
     ax.fill_between(datelist,theMin,theMax, facecolor='wheat')
     ax.plot(datelist,theMin,color='b')
     ax.plot(datelist,theMax,color='r')
     ax.plot(datelist,theMean,color='k')
     ax.xaxis.set_major_locator(months)
     ax.xaxis.set_major_formatter(theFormat)
     ax.xaxis.set_minor_locator(daysLocator)
     plt.ylabel('Daily range of ' + var)
     plt.title(title)
     fig.autofmt_xdate()
     if show: plt.show()


#------------- comparison plot of a daily statistic over a time interval
def compareDailyStat(date, dataList, var, start_date, end_date, leg = [], \
          stat='mean', title='', show=True):
     import matplotlib.pyplot as plt
     import matplotlib.dates as mdates
     import matplotlib
     matplotlib.rcParams['axes.color_cycle'] = ['r', 'k', 'c']
     years = mdates.YearLocator()   # every year
     months = mdates.MonthLocator()  # every month
     daysLocator = mdates.DayLocator()  # every day
     theFormat = mdates.DateFormatter('%Y-%b')
     # find indices of start and end dates
     indices = [i for i,x in enumerate(date) \
               if x.isoformat() == start_date \
               or x.isoformat() == end_date]
     if len(indices) < 2:
          print "dates not in range"
          return -1
     else:
          print "index range plotted: ", indices
     # for each day, process variable and compute statistic
     theStat = []
     for data in dataList:
          theStat.append(computeStatistic(var,stat,data,indices))
     # get requested dates 
     datelist = [day for day in date[indices[0]:indices[1]+1]]
     # make plot
     fig = plt.figure()
     ax = fig.add_subplot(111)
     ax.grid(True)
     # ax.plot(range(len(varlist)),varlist)
     for aStat in theStat:
          ax.plot(datelist,aStat)
     if len(leg) > 0: ax.legend(leg)
     ax.xaxis.set_major_locator(months)
     ax.xaxis.set_major_formatter(theFormat)
     ax.xaxis.set_minor_locator(daysLocator)
     plt.ylabel('Daily ' + stat + ' ' + var)
     plt.title(title)
     fig.autofmt_xdate()
     if show: plt.show()
