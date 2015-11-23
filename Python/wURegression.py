################################################################
################## REGRESSION MODELS ###########################
################################################################
#
###############################################################
################## SIMPLEST ONE-STATION MODEL #################
###############################################################
#
def oneCityModel(station, startDate, endDate, \
                 features, targetVar='TempMax', lag=1, scale=False):
     # build regression model to predict "variable" for a single
     # station using training data from only the same station 
     # between startdate and enddate
     # features is a list of variables to use as predictors
     import wUUtils as Util
     import numpy as np
     from sklearn import preprocessing
     from sklearn import linear_model
     # load target variable data
     target = Util.loadDailyVariableRange(station, startDate, endDate, \
                        targetVar, castFloat=True)
     # shift vector by lag
     target = target[lag:]
     # load feature data
     featureData = []
     for feature in features:
          # print("Adding " + feature)
          fd = Util.loadDailyVariableRange(station, startDate, endDate, \
                        feature, castFloat=True)
          # shorten vector by lag
          fd = fd[:(-lag)]
          featureData.append(fd)
     # convert target and features to np arrays
     target = np.array(target)
     featureData = (np.array(featureData)).T
     # rescale features
     scaler = None
     if scale:
          scaler = preprocessing.StandardScaler().fit(featureData)
          featureData = scaler.transform(featureData)          
     regr = linear_model.LinearRegression()
     regr.fit(featureData, target)
     model_params = {
            'station': station, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'regr': regr, \
            'lag': lag, \
            'scale': scale, \
            'scaler': scaler}
     # report regression results:
     print("R^2: " + str(regr.score(featureData,target)))
     if scale:
          print("Regression coefficients (scaled, sorted):")
          print("  intercept" + ":\t" + str(regr.intercept_))
          for ii in np.argsort(-np.abs(regr.coef_)):
               print("  " + features[ii] + ":\t" + str(regr.coef_[ii]))         
     else:
          print("Regression coefficients:")
          print("  intercept" + ":\t" + str(regr.intercept_))
          for ii in range(len(regr.coef_)):
               print("  " + features[ii] + ":\t" + str(regr.coef_[ii]))         
     return featureData, target, model_params

#
def oneCityPredict(model_params, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     import wUUtils as Util
     # extract city and feature data
     station = model_params['station']
     targetVar = model_params['targetVar']
     features = model_params['features']
     lag = model_params['lag']
     regr = model_params['regr']
     scale = model_params['scale']
     if scale:
          scaler = model_params['scaler']
     # build list of dates in datetime format
     date_list = Util.dateList(startDate, endDate)
     date_list = date_list[lag:]
     # if actual data available
     if actual:
          # load target variable data
          target = Util.loadDailyVariableRange(station, startDate, endDate, \
                             targetVar, castFloat=True)

          # "baseline" model is predicted target same as value on prediction day
          baseline = target[:(-lag)]
          baseline = np.array(baseline)
          
          # shift vector by lag
          target = target[lag:]
          target = np.array(target)
     else:
          target = None
     # load feature data
     featureData = []
     for feature in features:
          # print("Adding " + feature)
          fd = Util.loadDailyVariableRange(station, startDate, endDate, \
                        feature, castFloat=True)
          # shorten vector by lag
          fd = fd[:(-lag)]
          featureData.append(fd)
     # convert features to np arrays
     featureData = (np.array(featureData)).T
     if scale:
          featureData = scaler.transform(featureData)
     pred = regr.predict(featureData)
     if actual:
          print("R^2_mean:" + "\t" + str(regr.score(featureData,target)))
          sse = ((pred-target)**2).sum()
          ssm = ((baseline-target)**2).sum()
          print("R^2_base:" + "\t" + str(1 - sse/ssm))
          rmse = np.sqrt(((pred - target)**2).mean())
          rmse_base = np.sqrt(((baseline - target)**2).mean())
          print("RMSE:\t" + "\t" + str(rmse))
          print("RMSE_base:\t" + str(rmse_base))
          model_perf = {
               'R2_mean': regr.score(featureData,target), \
               'R2_base': 1 - sse/ssm, \
               'RMSE': rmse}
     return date_list, pred, target, model_perf

###############################################################
################## ONE-STATION "TAYLOR" MODEL #################
###############################################################
#
def oneCityTaylorModel(station, startDate, endDate, \
                       features, targetVar='TempMax', \
                       lag=1, order=0, verbose=True, scale=False):
     # build regression model to predict "variable" for a single
     # station using training data from only the same station 
     # between startdate and enddate
     # features is a list of variables to use as predictors
     # use a "Taylor expansion" by combining information from
     # order is the maximum order of derivative to use
     import numpy as np
     import wUUtils as Util
     from sklearn import preprocessing
     from sklearn import linear_model
     # load target variable data
     target = Util.loadDailyVariableRange(station, startDate, endDate, \
                        targetVar, castFloat=True)
     # shift vector by lag
     target = target[lag:]
     # load feature data
     featureData = []
     for feature in features:
          # print("Adding " + feature)
          fd = Util.loadDailyVariableRange(station, startDate, endDate, \
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
     # rescale features
     scaler = None
     if scale:
          scaler = preprocessing.StandardScaler().fit(featureData)
          featureData = scaler.transform(featureData)          
     regr = linear_model.LinearRegression()
     regr.fit(featureData, target)
     model_params = {
            'station': station, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'regr': regr, \
            'lag': lag, \
            'order': order, \
            'scale': scale, \
            'scaler': scaler}
     # report regression results:
     print("R^2: " + str(regr.score(featureData,target)))
     if verbose:
          if scale:
               print("Regression coefficients (scaled, sorted):")
               print("  intercept" + ":\t" + str(regr.intercept_))
               for ii in np.argsort(-np.abs(regr.coef_)):
                    ideriv = ii / len(features)
                    ifeat = ii - len(features)*ideriv
                    print("  " + str(ideriv) + 'th deriv of ' \
                            + features[ifeat] + ":\t" + str(regr.coef_[ii]))         
          else:
               print("Regression coefficients:")
               print("  intercept" + ":\t" + str(regr.intercept_))
               for ideriv in range(order+1):
                    print("  " + str(ideriv) + "th derivative:")
                    for ii, feature in enumerate(features):
                         column = len(features)*ideriv + ii
                         print("    " + feature + ":\t" + str(regr.coef_[column]))
     return featureData, target, model_params

#
def oneCityTaylorPredict(model_params, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     import wUUtils as Util
     # extract city and feature data
     station = model_params['station']
     targetVar = model_params['targetVar']
     features = model_params['features']
     regr = model_params['regr']
     lag = model_params['lag']
     order = model_params['order']
     scale = model_params['scale']
     if scale:
          scaler = model_params['scaler']
     # build list of dates in datetime format
     date_list = Util.dateList(startDate, endDate)
     date_list = date_list[(lag+order):]
     # if actual data available
     if actual:
          # load target variable data
          target = Util.loadDailyVariableRange(station, startDate, endDate, \
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
     for feature in features:
          # print("Adding " + feature)
          fd = Util.loadDailyVariableRange(station, startDate, endDate, \
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
     # convert features to np arrays
     featureData = (np.array(featureData)).T
     if scale:
          featureData = scaler.transform(featureData)
     pred = regr.predict(featureData)
     if actual:
          print("R^2_mean:" + "\t" + str(regr.score(featureData,target)))
          sse = ((pred-target)**2).sum()
          ssm = ((baseline-target)**2).sum()
          print("R^2_base:" + "\t" + str(1 - sse/ssm))
          rmse = np.sqrt(((pred - target)**2).mean())
          rmse_base = np.sqrt(((baseline - target)**2).mean())
          print("RMSE:\t" + "\t" + str(rmse))
          print("RMSE_base:\t" + str(rmse_base))
          model_perf = {
               'R2_mean': regr.score(featureData,target), \
               'R2_base': 1 - sse/ssm, \
               'RMSE': rmse}
     return date_list, pred, target, model_perf


###############################################################
################## MULTI-STATION "TAYLOR" MODEL ###############
###############################################################
#
def multiCityTaylorModel(stations, startDate, endDate, \
                     features, targetVar='TempMax', \
                     lag=1, order=0, verbose=False, scale=False):
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
     import wUUtils as Util
     from sklearn import preprocessing
     from sklearn import linear_model
     # load target variable data
     target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                        targetVar, castFloat=True)
     # shift vector by lag
     target = target[lag:]
     # load feature data
     featureData = []
     for station in stations:
          for feature in features:
               # print("Adding " + feature + " from " + station)
               fd = Util.loadDailyVariableRange(station, startDate, endDate, \
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
     # rescale features
     scaler = None
     if scale:
          scaler = preprocessing.StandardScaler().fit(featureData)
          featureData = scaler.transform(featureData)          
     # fit regression model
     regr = linear_model.LinearRegression()
     regr.fit(featureData, target)
     model_params = {
            'stations': stations, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'regr': regr, \
            'lag': lag, \
            'order': order, \
            'scale': scale, \
            'scaler': scaler}
     # report regression results:
     print("R^2: " + str(regr.score(featureData,target)))
     if verbose:
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
     return featureData, target, model_params

#
def multiCityTaylorPredict(model_params, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     import wUUtils as Util
     # extract city and feature data
     stations = model_params['stations']
     targetVar = model_params['targetVar']
     features = model_params['features']
     regr = model_params['regr']
     lag = model_params['lag']
     order = model_params['order']
     scale = model_params['scale']
     if scale:
          scaler = model_params['scaler']
     # build list of dates in datetime format
     date_list = Util.dateList(startDate, endDate)
     date_list = date_list[(lag+order):]
     # if actual data available
     if actual:
          # load target variable data
          target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
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
               fd = Util.loadDailyVariableRange(station, startDate, endDate, \
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
     # convert features to np arrays
     featureData = (np.array(featureData)).T
     if scale:
          featureData = scaler.transform(featureData)
     pred = regr.predict(featureData)
     if actual:
          print("R^2_mean:" + "\t" + str(regr.score(featureData,target)))
          sse = ((pred-target)**2).sum()
          ssm = ((baseline-target)**2).sum()
          print("R^2_base:" + "\t" + str(1 - sse/ssm))
          rmse = np.sqrt(((pred - target)**2).mean())
          print("RMSE:\t" + "\t" + str(rmse))
          model_perf = {
               'R2_mean': regr.score(featureData,target), \
               'R2_base': 1 - sse/ssm, \
               'RMSE': rmse}
     else:
          model_perf = None
     return date_list, pred, target, model_perf

###############################################################
################## MULTI-STATION MODEL W INTERACTIONS #########
###############################################################
#
def multiCityInteractionModel(stations, startDate, endDate, \
                     features, targetVar='TempMax', \
                     lag=1, order=0, verbose=False, scale=False):
     # build regression model to predict "variable" for a single
     # station using training data from multiple stations 
     # between startdate and enddate.  Uses a "Taylor expansion" 
     # by combining information from several days (higher order
     # time derivatives)
     #
     # stations: a list of station codes, the first entry is
     #             the station for which forecast is generated
     # features: a list of variables to use as predictors
     #         *** if a feature string contains a ":" it is parsed as
     #             an interaction between two features ...
     #         *** features in interaction terms pre-scaled! 
     #      lag: the number of days in the future to forecast
     #    order: the number of days in the past to include
     #           (also maximum order of time derivative)
     import numpy as np
     import wUUtils as Util
     from sklearn import preprocessing
     from sklearn import linear_model
     # load target variable data
     target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                        targetVar, castFloat=True)
     # shift vector by lag
     target = target[lag:]
     # load feature data
     featureData = []
     prescalers = []
     for station in stations:
          for feature in features:
	       # check if feature contains an interaction
	       if ':' in feature:
                    feat1 = feature.split(':')[0]
		    feat2 = feature.split(':')[1]
		    fd1 = Util.loadDailyVariableRange(station, startDate, endDate, \
				    feat1, castFloat=True)
		    fd2 = Util.loadDailyVariableRange(station, startDate, endDate, \
				    feat2, castFloat=True)
		    prescaler1 = preprocessing.StandardScaler().fit(fd1)
		    fd1 = prescaler1.transform(fd1)
		    prescaler2 = preprocessing.StandardScaler().fit(fd2)
		    fd2 = prescaler2.transform(fd2)
		    # save prescaler objects (for prediction)
		    prescalers.append([prescaler1,prescaler2])
		    # compute interaction
		    fd = (np.array(fd1)*np.array(fd2)).tolist()
	       else:
                    fd = Util.loadDailyVariableRange(station, startDate, endDate, \
                                  feature, castFloat=True)
		    prescalers.append(None)
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
     # rescale features
     scaler = None
     if scale:
          scaler = preprocessing.StandardScaler().fit(featureData)
          featureData = scaler.transform(featureData)          
     # fit regression model
     regr = linear_model.LinearRegression()
     regr.fit(featureData, target)
     model_params = {
            'stations': stations, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'regr': regr, \
            'lag': lag, \
            'order': order, \
            'scale': scale, \
            'scaler': scaler, \
	    'prescalers': prescalers}
     # report regression results:
     print("R^2: " + str(regr.score(featureData,target)))
     if verbose:
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
     return featureData, target, model_params

#
def multiCityInteractionPredict(model_params, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     import wUUtils as Util
     # extract city and feature data
     stations = model_params['stations']
     targetVar = model_params['targetVar']
     features = model_params['features']
     regr = model_params['regr']
     lag = model_params['lag']
     order = model_params['order']
     scale = model_params['scale']
     prescalers = model_params['prescalers']
     if scale:
          scaler = model_params['scaler']
     # build list of dates in datetime format
     date_list = Util.dateList(startDate, endDate)
     date_list = date_list[(lag+order):]
     # if actual data available
     if actual:
          # load target variable data
          target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
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
     idata = 0
     for station in stations:
          for feature in features:
	       # check if feature contains an interaction
	       if ':' in feature:
                    feat1 = feature.split(':')[0]
		    feat2 = feature.split(':')[1]
		    fd1 = Util.loadDailyVariableRange(station, startDate, endDate, \
				    feat1, castFloat=True)
		    fd2 = Util.loadDailyVariableRange(station, startDate, endDate, \
				    feat2, castFloat=True)
		    # rescale factors in interaction
		    prescaler1, prescaler2 = prescalers[idata]
		    fd1 = prescaler1.transform(fd1)
		    fd2 = prescaler2.transform(fd2)
		    # compute interaction
		    fd = (np.array(fd1)*np.array(fd2)).tolist()
	       else:
                    fd = Util.loadDailyVariableRange(station, startDate, endDate, \
                                  feature, castFloat=True)
               # shorten vector by lag
               fd = fd[:(-lag)]
               featureData.append(fd)
               # increment feature counter
	       idata += 1
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
     # convert features to np arrays
     featureData = (np.array(featureData)).T
     if scale:
          featureData = scaler.transform(featureData)
     pred = regr.predict(featureData)
     if actual:
          print("R^2_mean:" + "\t" + str(regr.score(featureData,target)))
          sse = ((pred-target)**2).sum()
          ssm = ((baseline-target)**2).sum()
          print("R^2_base:" + "\t" + str(1 - sse/ssm))
          rmse = np.sqrt(((pred - target)**2).mean())
          print("RMSE:\t" + "\t" + str(rmse))
          model_perf = {
               'R2_mean': regr.score(featureData,target), \
               'R2_base': 1 - sse/ssm, \
               'RMSE': rmse}
     else:
          model_perf = None
     return date_list, pred, target, model_perf

###############################################################
################## ADVECTION MODEL ############################
###############################################################
#
def advectionTaylorModel(stations, startDate, endDate, \
                     features, targetVar='TempMax', \
                     lag=1, order=0, verbose=False):
     # build regression model to predict "variable" for a single
     # station using training data from multiple stations 
     # between startdate and enddate.  Uses a "Taylor expansion" 
     # by combining information from several days (higher order
     # time derivatives)
     #
     # for each variable, at target station, use value, and
     # at other stations, only the projection of its gradient 
     # in the direction of the target station
     # 
     # stations: a list of station codes, the first entry is
     #           the target station (for which forecast is generated)
     # features: a list of variables to use as predictors
     #      lag: the number of days in the future to forecast
     #    order: the number of days in the past to include
     #           (also maximum order of time derivative)
     import numpy as np
     import wUUtils as Util
     import wUAdvection as Adv
     reload(Adv)
     from sklearn import linear_model
     # load target variable data
     target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                        targetVar, castFloat=True)
     # shift vector by lag
     target = target[lag:]
     # load feature data
     featureData = []
     # add data for target station
     for feature in features:
          fd = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                             feature, castFloat=True)
          # shorten vector by lag
          fd = fd[:(-lag)]
          featureData.append(fd)
     # for other stations, add the advection of each feature in the
     # direction of the target station
     for station in stations[1:]:
          for feature in features:
               # print("Adding " + feature + " from " + station)
               fd, uVec = Adv.dDeriv(stations[0], station, \
                                     feature, startDate, endDate)
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
            'regr': regr, \
            'lag': lag, \
            'order': order}
     # report regression results:
     print("R^2: " + str(regr.score(featureData,target)))
     if verbose:
          print("Regression coefficients:")
          print("  intercept" + ":\t" + str(regr.intercept_))
          column = 0
          for ideriv in range(order+1):
               print("  " + str(ideriv) + "th derivative:")
               for jj, station in enumerate(stations):
                    if jj > 0:
                         print("    Station (Adv): " + station)
                    else:
                         print("    Station: " + station)
                    for ii, feature in enumerate(features):
                         print("       " + feature + ":\t" + str(regr.coef_[column]))
                         column += 1
     return featureData, target, model_params

#
def advectionTaylorPredict(model_params, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     import wUUtils as Util
     import wUAdvection as Adv
     # extract city and feature data
     stations = model_params['stations']
     targetVar = model_params['targetVar']
     features = model_params['features']
     regr = model_params['regr']
     lag = model_params['lag']
     order = model_params['order']
     # build list of dates in datetime format
     date_list = Util.dateList(startDate, endDate)
     date_list = date_list[(lag+order):]
     # if actual data available
     if actual:
          # load target variable data
          target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
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
     # add data for target station
     for feature in features:
          fd = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                             feature, castFloat=True)
          # shorten vector by lag
          fd = fd[:(-lag)]
          featureData.append(fd)
     # for other stations, add the advection of each feature in the
     # direction of the target station
     for station in stations[1:]:
          for feature in features:
               # print("Adding " + feature + " from " + station)
               fd, uVec = Adv.dDeriv(stations[0], station, \
                                     feature, startDate, endDate)
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
     # convert features to np arrays
     featureData = (np.array(featureData)).T
     pred = regr.predict(featureData)
     if actual:
          print("R^2_mean:" + "\t" + str(regr.score(featureData,target)))
          sse = ((pred-target)**2).sum()
          ssm = ((baseline-target)**2).sum()
          print("R^2_base:" + "\t" + str(1 - sse/ssm))
          rmse = np.sqrt(((pred - target)**2).mean())
          print("RMSE:\t" + "\t" + str(rmse))
          model_perf = {
                    'R2_mean': regr.score(featureData,target), \
                    'R2_base': 1 - sse/ssm, \
                    'RMSE': rmse}
     else:
          model_perf = None
     return date_list, pred, target, model_perf
     

###############################################################
################## MODEL USING PCA ############################
###############################################################
#
def pcaTaylorModel(stations, startDate, endDate, \
                   features, ncomp=None, targetVar='TempMax', \
                   lag=1, order=0, smooth_window=0, verbose=False):
     # build regression model to predict "variable" for a single
     # station using training data from multiple stations 
     # between startdate and enddate.
     #
     # The set of values of each feature at all stations is converted
     # to a truncated list of principal components for purposes of 
     # feature-reduction and reduction of multicolinearity 
     # 
     # Uses a "Taylor expansion" by combining information from 
     # several days (higher order time derivatives)
     #
     # stations: a list of station codes, the first entry is
     #             the station for which forecast is generated
     # features: a list of variables to use as predictors
     #    ncomp: a list of same length as features containing the
     #           number of PCA to keep for each feature
     #      lag: the number of days in the future to forecast
     #    order: the number of days in the past to include
     #           (also maximum order of time derivative)
     import numpy as np
     import wUUtils as Util
     import wUPCA
     reload(wUPCA)
     from sklearn import preprocessing
     from sklearn import linear_model
     # load target variable data
     target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                        targetVar, castFloat=True)
     if smooth_window > 0:
          target = Util.smooth(target, smooth_window)
     # shift vector by lag
     target = target[lag:]
     # load features data and compute PC
     pcaData, transform_params = wUPCA.pcaConvert(stations, features, \
                                                  startDate, endDate, ncomp)
     # flatten featureData into single list of lists, while shortening by lag
     featureData = [data[:(-lag)] for dataList in pcaData for data in dataList] 
     if smooth_window > 0:
          for data in featureData:
               data = Util.smooth(data,smooth_window)
     # number of PC-transformed features
     if ncomp == None:
          nfeat = len(stations)*len(features)
     else:
          nfeat = sum(ncomp) 
     # add in "derivative" terms
     for ideriv in range(1,order+1):
          for ii in range(nfeat):
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

     # fit regression model
     regr = linear_model.LinearRegression()
     regr.fit(featureData, target)
     model_params = {
            'stations': stations, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'regr': regr, \
            'lag': lag, \
            'order': order, \
            'smooth_window': smooth_window, \
            'transform_params': transform_params}
     # report regression results:
     print("R^2: " + str(regr.score(featureData,target)))
     if verbose:
          print("Regression coefficients:")
          print("  intercept" + ":\t" + str(regr.intercept_))
          column = 0
          for ideriv in range(order+1):
               print("  " + str(ideriv) + "th derivative:")
               for ii, feature in enumerate(features):
                    print("    " + feature)
                    if ncomp == None:
                         nc = len(stations)
                    else:
                         nc = ncomp[ii]
                    for jj in range(nc):
                         print("      PC " + str(jj) + " :\t" + str(regr.coef_[column]))
                         column += 1
     return featureData, target, model_params

#
def pcaTaylorPredict(model_params, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     import wUUtils as Util
     import wUPCA
     reload(wUPCA)
     # extract city and feature data
     stations = model_params['stations']
     targetVar = model_params['targetVar']
     features = model_params['features']
     regr = model_params['regr']
     lag = model_params['lag']
     order = model_params['order']
     transform_params = model_params['transform_params']
     ncomp = transform_params['ncomp']
     # build list of dates in datetime format
     date_list = Util.dateList(startDate, endDate)
     date_list = date_list[(lag+order):]
     # if actual data available
     if actual:
          # load target variable data
          target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                             targetVar, castFloat=True)
          # "baseline" model is predicted target same as value on prediction day
          baseline = target[order:(-lag)]
          baseline = np.array(baseline)
          # shift vector by lag
          target = target[lag:]
          target = np.array(target)
     else:
          target = None

     # load features data and compute PC
     pcaData = wUPCA.pcaPredict(transform_params, startDate, endDate)
     # flatten featureData into single list of lists, while shortening by lag
     featureData = [data[:(-lag)] for dataList in pcaData for data in dataList] 
     # number of PC-transformed features
     nfeat = sum(ncomp) 
     # add in "derivative" terms
     for ideriv in range(1,order+1):
          for ii in range(nfeat):
               # print("Adding " + str(ideriv) + " derivative of " + feature[jfeat])
               fd = np.diff(featureData[ii],n=ideriv)
               featureData.append(fd)
     # shorten vectors to length of highest order derivative
     nrows = len(featureData[-1])
     for column in range(len(featureData)):
          featureData[column] = featureData[column][-nrows:]
     if actual:
          target = target[-nrows:]
     # convert features to np arrays
     featureData = (np.array(featureData)).T
     pred = regr.predict(featureData)
     if actual:
          print("R^2_mean:" + "\t" + str(regr.score(featureData,target)))
          sse = ((pred-target)**2).sum()
          ssm = ((baseline-target)**2).sum()
          print("R^2_base:" + "\t" + str(1 - sse/ssm))
          rmse = np.sqrt(((pred - target)**2).mean())
          print("RMSE:\t" + "\t" + str(rmse))
          model_perf = {
               'R2_mean': regr.score(featureData,target), \
               'R2_base': 1 - sse/ssm, \
               'RMSE': rmse}
     else:
          model_perf = None
     return date_list, pred, target, model_perf

###############################################################
################## STATION INTERCOMPARISON ####################
###############################################################
#
def compareStationsOneCity(stations, \
                           startTrain, endTrain, startTest, endTest, \
                           features, targetVar='TempMax', \
                           lag=1, order=0):
     # list of performance measures on test set
     perfList = []
     for targetStation in stations:
          print('\n' + targetStation + ':')
          # train model
          featureData, target, model_params = \
               oneCityTaylorModel(targetStation, \
                                  startTrain, endTrain, \
                                  features, targetVar, \
                                  lag, order, verbose=False)
          # test model
          date_list, pred, target, model_perf = \
               oneCityTaylorPredict(model_params, \
                                    startTest, endTest, \
                                    actual = True)
          model_perf['station'] = targetStation
          perfList.append(model_perf)
     return perfList

#
def compareStationsMultiCity(stations, \
                             startTrain, endTrain, startTest, endTest, \
                             features, targetVar='TempMax', \
                             lag=1, order=0):
     # list of performance measures on test set
     perfList = []
     for targetStation in stations:
          print('\n' + targetStation + ':')
          # move targetStation to first in list of stations
          otherStations = [s for s in stations if s != targetStation]
          sortedStations = [targetStation] + otherStations
          # train model
          featureData, target, model_params = \
               multiCityTaylorModel(sortedStations, \
                                    startTrain, endTrain, \
                                    features, targetVar, \
                                    lag, order, verbose = False)
          # test model
          date_list, pred, target, model_perf = \
               multiCityTaylorPredict(model_params, \
                                      startTest, endTest, \
                                      actual = True)
          model_perf['station'] = targetStation
          perfList.append(model_perf)
     return perfList

###############################################################
################## PLOT RESULTS ###############################
###############################################################
#
def plotModelPred(date_list, pred, target, startIndex=0, endIndex=0, showIt=True):
     # plot a prediction and the actual values versus date
     import matplotlib.pyplot as plt
     fig = plt.figure()
     # bounds:
     sI = startIndex
     if endIndex == 0:
          eI = len(date_list)
     else:
          eI = endIndex
     # create new figure
     fig = plt.figure()
     ax = fig.add_subplot(111)
     # line and scatter plot of true values
     plt.plot(date_list[sI:eI], \
              target[sI:eI], color='black')
     tp = plt.scatter(date_list[sI:eI], \
              target[sI:eI], color='black')
     # line and scatter plot of predictions
     plt.plot(date_list[sI:eI], \
          pred[sI:eI], color='red')
     pp = plt.scatter(date_list[sI:eI], \
              pred[sI:eI], color='red')
     plt.legend((tp, pp),('Truth','Predicted'))
     fig.autofmt_xdate()
     if showIt:
          plt.show()
     return ax
     
#
def extractCoeffs(regr, model_params, exFeature, exOrder):
     # given regression model regr, extract coefficients
     # for all stations for the given feature and order
     # (e.g. for plotting)
     stations = model_params['stations']
     features = model_params['features']
     order = model_params['order']
     # check order and feature
     if exFeature not in features:
          print('Feature not found!')
          return -1
     if exOrder > order:
          print('Order out of range!')
          return -2
     # extract the relevant coefficients from regr
     featureIndex = features.index(exFeature)
     startindex = exOrder*len(stations)*len(features)+featureIndex
     endindex = (exOrder+1)*len(stations)*len(features)
     return (regr.coef_[startindex:endindex:len(features)]).tolist()


     
