################################################################
################## REGRESSION MODELS ###########################
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

def dateList(startDate, endDate):
     # generate list of datetime objects for a range of dates
     # (mostly for plotting purposes)
     import datetime
     day0 = datetime.datetime.strptime(startDate,"%Y-%m-%d")
     dayN = datetime.datetime.strptime(endDate,"%Y-%m-%d")
     N = (dayN-day0).days
     date_list = [day0 + datetime.timedelta(days = n) for n in range(0,N+1)]
     return date_list

###############################################################
################## SIMPLEST ONE-STATION MODEL #################
###############################################################
#
def oneCityModel(station, startDate, endDate, \
                 features, targetVar='TempMax', lag=1):
     # build regression model to predict "variable" for a single
     # station using training data from only the same station 
     # between startdate and enddate
     # features is a list of variables to use as predictors
     import numpy as np
     from sklearn import linear_model
     # load target variable data
     target = loadDailyVariableRange(station, startDate, endDate, \
                        targetVar, castFloat=True)
     # shift vector by lag
     target = target[lag:]
     # load feature data
     featureData = []
     for feature in features:
          # print("Adding " + feature)
          fd = loadDailyVariableRange(station, startDate, endDate, \
                        feature, castFloat=True)
          # shorten vector by lag
          fd = fd[:(-lag)]
          featureData.append(fd)
     # convert target and features to np arrays
     target = np.array(target)
     featureData = (np.array(featureData)).T
     regr = linear_model.LinearRegression()
     regr.fit(featureData, target)
     model_params = {
            'station': station, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'lag': lag }
     # report regression results:
     print("R^2: " + str(regr.score(featureData,target)))
     print("Regression coefficients:")
     print("  intercept" + ":\t" + str(regr.intercept_))
     for ii, feature in enumerate(features):
          print("  " + feature + ":\t" + str(regr.coef_[ii]))         
     return featureData, target, regr, model_params

#
def oneCityPredict(regr, model_params, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     # extract city and feature data
     station = model_params['station']
     targetVar = model_params['targetVar']
     features = model_params['features']
     lag = model_params['lag']
     # build list of dates in datetime format
     date_list = dateList(startDate, endDate)
     date_list = date_list[lag:]
     # if actual data available
     if actual:
          # load target variable data
          target = loadDailyVariableRange(station, startDate, endDate, \
                             targetVar, castFloat=True)
          # shift vector by lag
          target = target[lag:]
          target = np.array(target)
     else:
          target = None
     # load feature data
     featureData = []
     for feature in features:
          # print("Adding " + feature)
          fd = loadDailyVariableRange(station, startDate, endDate, \
                        feature, castFloat=True)
          # shorten vector by lag
          fd = fd[:(-lag)]
          featureData.append(fd)
     # convert target and features to np arrays
     featureData = (np.array(featureData)).T
     pred = regr.predict(featureData)
     if actual:
          print("R^2: " + str(regr.score(featureData,target)))
     return date_list, pred, target

###############################################################
################## ONE-STATION "TAYLOR" MODEL #################
###############################################################
#
def oneCityTaylorModel(station, startDate, endDate, \
                     features, targetVar='TempMax', lag=1, order=0):
     # build regression model to predict "variable" for a single
     # station using training data from only the same station 
     # between startdate and enddate
     # features is a list of variables to use as predictors
     # use a "Taylor expansion" by combining information from
     # order is the maximum order of derivative to use
     import numpy as np
     from sklearn import linear_model
     # load target variable data
     target = loadDailyVariableRange(station, startDate, endDate, \
                        targetVar, castFloat=True)
     # shift vector by lag
     target = target[lag:]
     # load feature data
     featureData = []
     for feature in features:
          # print("Adding " + feature)
          fd = loadDailyVariableRange(station, startDate, endDate, \
                        feature, castFloat=True)
          # shorten vector by lag
          fd = fd[:(-lag)]
          featureData.append(fd)
     # add in "derivative" terms
     for ideriv in range(1,order+1):
          for jfeat in range(len(features)):
               # print("Adding " + str(ideriv) + " derivative of " + feature[jfeat])
               fd = np.diff(featureData[jfeat],n=ideriv)
               featureData.append(fd)
     # shorten vectors to length of highest order derivative
     nrows = len(featureData[-1])
     # print("nrows ... " + str(nrows))
     for column in range(len(featureData)):
          featureData[column] = featureData[column][-nrows:]
     target = target[-nrows:]
     # convert target and features to np arrays
     target = np.array(target)
     featureData = (np.array(featureData)).T
     regr = linear_model.LinearRegression()
     regr.fit(featureData, target)
     model_params = {
            'station': station, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'lag': lag,
            'order': order}
     # report regression results:
     print("R^2: " + str(regr.score(featureData,target)))
     print("Regression coefficients:")
     print("  intercept" + ":\t" + str(regr.intercept_))
     for ideriv in range(order+1):
          print("  " + str(ideriv) + "th derivative:")
          for ii, feature in enumerate(features):
               column = len(features)*ideriv + ii
               print("    " + feature + ":\t" + str(regr.coef_[column]))
     return featureData, target, regr, model_params

#
def oneCityTaylorPredict(regr, model_params, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     # extract city and feature data
     station = model_params['station']
     targetVar = model_params['targetVar']
     features = model_params['features']
     lag = model_params['lag']
     order = model_params['order']
     # build list of dates in datetime format
     date_list = dateList(startDate, endDate)
     date_list = date_list[(lag+order):]
     # if actual data available
     if actual:
          # load target variable data
          target = loadDailyVariableRange(station, startDate, endDate, \
                             targetVar, castFloat=True)
          # shift vector by lag
          target = target[lag:]
          target = np.array(target)
     else:
          target = None
     # load feature data
     featureData = []
     for feature in features:
          # print("Adding " + feature)
          fd = loadDailyVariableRange(station, startDate, endDate, \
                        feature, castFloat=True)
          # shorten vector by lag
          fd = fd[:(-lag)]
          featureData.append(fd)
     # add in "derivative" terms
     for ideriv in range(1,order+1):
          for jfeat in range(len(features)):
               fd = np.diff(featureData[jfeat],n=ideriv)
               featureData.append(fd)
     # shorten vectors to length of highest order derivative
     nrows = len(featureData[-1])
     # print("nrows ... " + str(nrows))
     for column in range(len(featureData)):
          featureData[column] = featureData[column][-nrows:]
     if actual:
          target = target[-nrows:]
     # convert target and features to np arrays
     featureData = (np.array(featureData)).T
     pred = regr.predict(featureData)
     if actual:
          print("R^2: " + str(regr.score(featureData,target)))
     return date_list, pred, target


###############################################################
################## MULTI-STATION "TAYLOR" MODEL ###############
###############################################################
#
def multiCityTaylorModel(stations, startDate, endDate, \
                     features, targetVar='TempMax', lag=1, order=0):
     # build regression model to predict "variable" for a single
     # station using training data from multiple stations 
     # between startdate and enddate.  Uses a "Taylor expansion" 
     # by combining information from several days (higher order
     # time derivatives)
     #
     # stations: a list of station codes, the first entry is
     #             the station for which forecast is generated
     # features: a list of variables to use as predictors
     #      lag: the number of days in the future to forecast
     #    order: the number of days in the past to include
     #           (also maximum order of time derivative)
     import numpy as np
     from sklearn import linear_model
     # load target variable data
     target = loadDailyVariableRange(stations[0], startDate, endDate, \
                        targetVar, castFloat=True)
     # shift vector by lag
     target = target[lag:]
     # load feature data
     featureData = []
     for station in stations:
          for feature in features:
               # print("Adding " + feature + " from " + station)
               fd = loadDailyVariableRange(station, startDate, endDate, \
                             feature, castFloat=True)
               # shorten vector by lag
               fd = fd[:(-lag)]
               featureData.append(fd)
     # add in "derivative" terms
     for ideriv in range(1,order+1):
          ncols = len(stations)*len(features)
          for ii in range(ncols):
               # print("Adding " + str(ideriv) + " derivative of " + feature[jfeat])
               fd = np.diff(featureData[ii],n=ideriv)
               featureData.append(fd)
     # shorten vectors to length of highest order derivative
     nrows = len(featureData[-1])
     for column in range(len(featureData)):
          featureData[column] = featureData[column][-nrows:]
     target = target[-nrows:]
     # convert target and features to np arrays
     target = np.array(target)
     featureData = (np.array(featureData)).T
     regr = linear_model.LinearRegression()
     regr.fit(featureData, target)
     model_params = {
            'stations': stations, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'lag': lag,
            'order': order}
     # report regression results:
     print("R^2: " + str(regr.score(featureData,target)))
     print("Regression coefficients:")
     print("  intercept" + ":\t" + str(regr.intercept_))
     column = 0
     for ideriv in range(order+1):
          print("  " + str(ideriv) + "th derivative:")
          for jj, station in enumerate(stations):
               print("    Station: " + station)
               for ii, feature in enumerate(features):
                    print("       " + feature + ":\t" + str(regr.coef_[column]))
                    column += 1
     return featureData, target, regr, model_params

#
def multiCityTaylorPredict(regr, model_params, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     # extract city and feature data
     stations = model_params['stations']
     targetVar = model_params['targetVar']
     features = model_params['features']
     lag = model_params['lag']
     order = model_params['order']
     # build list of dates in datetime format
     date_list = dateList(startDate, endDate)
     date_list = date_list[(lag+order):]
     # if actual data available
     if actual:
          # load target variable data
          target = loadDailyVariableRange(stations[0], startDate, endDate, \
                             targetVar, castFloat=True)
          # "baseline" model is predicted target same as value on prediction day
          baseline = target[order:(-lag)]
          baseline = np.array(baseline)
          # shift vector by lag
          target = target[lag:]
          target = np.array(target)
     else:
          target = None
     # load feature data
     featureData = []
     for station in stations:
          for feature in features:
               # print("Adding " + feature + " from " + station)
               fd = loadDailyVariableRange(station, startDate, endDate, \
                             feature, castFloat=True)
               # shorten vector by lag
               fd = fd[:(-lag)]
               featureData.append(fd)
     # add in "derivative" terms
     for ideriv in range(1,order+1):
          ncols = len(stations)*len(features)
          for ii in range(ncols):
               # print("Adding " + str(ideriv) + " derivative of " + feature[jfeat])
               fd = np.diff(featureData[ii],n=ideriv)
               featureData.append(fd)
     # shorten vectors to length of highest order derivative
     nrows = len(featureData[-1])
     for column in range(len(featureData)):
          featureData[column] = featureData[column][-nrows:]
     if actual:
          target = target[-nrows:]
     # convert target and features to np arrays
     featureData = (np.array(featureData)).T
     pred = regr.predict(featureData)
     if actual:
          print("R^2_mean:" + "\t" + str(regr.score(featureData,target)))
          sse = ((pred-target)**2).sum()
          ssm = ((baseline-target)**2).sum()
          print("R^2_base:" + "\t" + str(1 - sse/ssm))
          rmse = np.sqrt(((pred - target)**2).mean())
          print("RMSE:\t" + "\t" + str(rmse))
     return date_list, pred, target

###############################################################
################## PLOT RESULTS ###############################
###############################################################
#
def plotModelPred(date_list, pred, target):
     # plot a prediction and the actual values versus date
     import matplotlib.pyplot as plt
     # create new figure
     fig = plt.figure()
     ax = fig.add_subplot(111)
     # line and scatter plot of true values
     plt.plot(date_list, target, color='black')
     tp = plt.scatter(date_list, target, color='black')
     # line and scatter plot of predictions
     plt.plot(date_list, pred, color='red')
     pp = plt.scatter(date_list, pred, color='red')
     plt.legend((tp, pp),('Truth','Predicted'))
     plt.show()
     return ax
     
     
