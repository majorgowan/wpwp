###############################################################
################## REGRESSION MODEL ###########################
###############################################################
#
def loadDailyVariableRange(station, startDate, endDate, \
                           variable, castFloat=False):
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
     import datetime
     day0 = datetime.datetime.strptime(startDate,"%Y-%m-%d")
     dayN = datetime.datetime.strptime(endDate,"%Y-%m-%d")
     N = (dayN-day0).days
     date_list = [day0 + datetime.timedelta(days = n) for n in range(0,N+1)]
     return date_list
     
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
     return date_list, pred, target

#
def plotModelPred(date_list, pred, target):
     import matplotlib.pyplot as plt
     # create new figure
     fig = plt.figure()
     # line and scatter plot of true values
     plt.plot(date_list, target, color='black')
     plt.scatter(date_list, target, color='black')
     # line and scatter plot of predictions
     plt.plot(date_list, pred, color='red')
     plt.scatter(date_list, pred, color='red')
     plt.show()
     
     