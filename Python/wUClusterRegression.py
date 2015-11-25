###############################################################
################## CLUSTER REGRESSION #########################
###############################################################
#
def clusterRegression(stations, startDate, endDate, \
                      features, clusterFeatures=None, \
                      nclusters=1, ranseed=666, \
                      targetVar='TempMax', \
                      lag=1, order=0, scale=False, verbose=False):
     # build regression model to predict a variable for a single
     # station using training data from multiple stations 
     # between startdate and enddate.  Uses a "Taylor expansion" 
     # by combining information from several days (higher order
     # time derivatives)
     #
     #   stations: a list of station codes, the first entry is
     #             the station for which forecast is generated
     #   features: a list of variables to use as predictors
     #         *** if a feature string contains a ":" it is parsed as
     #             an interaction between two features ...
     #         *** features in interaction terms pre-scaled!
     # clusterFeatures: subset of features with respect to which
     #             k-means clustering is applied before training
     #             regression models
     #  nclusters: number of clusters to compute
     #        lag: the number of days in the future to forecast
     #      order: the number of days in the past to include
     #             (also maximum order of time derivative)
     import wUCluster as Clust
     reload(Clust)
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

     # apply k-means clustering
     if clusterFeatures is not None:
          classes, clusterParams = Clust.clusterFeatureData(featureData, stations, features, \
                                                            clusterFeatures, nclusters, \
                                                            ranseed)
          classes, featureClusters = Clust.assignClustersAllFeatures(featureData, clusterParams)
          targetClusters = []
          for cl in range(nclusters):
               targetClusters.append([t for i,t in enumerate(target) if classes[i] == cl])
     else:
          # everything is one cluster
          classes = range(len(target))
          featureClusters = [featureData]
          targetClusters = [target]
          clusterParams = { 'nclusters': 1 }

     # train separate regression model for each cluster
     regrs = []
     scalers = []
     for icl in range(nclusters):
          # convert features and target to arrays
          featureClusters[icl] = (np.array(featureClusters[icl])).T
          targetClusters[icl] = np.array(targetClusters[icl])

          scaler = None
          if scale:
               scaler = preprocessing.StandardScaler().fit(featureClusters[icl])
               featureClusters[icl] = scaler.transform(featureClusters[icl])
          scalers.append(scaler)
     
          regr = linear_model.LinearRegression()
          regr.fit(featureClusters[icl], targetClusters[icl])
          regrs.append(regr)
          print('Cluster %d, nrows %d, R^2 %f' \
                       % (icl, \
                          len(targetClusters[icl]), \
                          regr.score(featureClusters[icl],targetClusters[icl])) )
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

     # save model parameters
     modelParams = {
            'stations': stations, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'regrs': regrs, \
            'clusterParams': clusterParams, \
            'classes': classes, \
            'lag': lag, \
            'order': order, \
            'scale': scale, \
            'scalers': scalers, \
            'prescalers': prescalers}
     return featureData, target, modelParams


#
def clusterRegressionPredict(modelParams, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import wUCluster as Clust
     reload(Clust)
     import numpy as np
     import wUUtils as Util
     # extract city and feature data
     stations = modelParams['stations']
     targetVar = modelParams['targetVar']
     features = modelParams['features']
     regrs = modelParams['regrs']
     clusterParams = modelParams['clusterParams']
     nclusters = clusterParams['nclusters']
     lag = modelParams['lag']
     order = modelParams['order']
     scale = modelParams['scale']
     prescalers = modelParams['prescalers']
     scalers = modelParams['scalers']

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

     # allocate features to clusters
     if clusterParams['nclusters'] > 1:
          classes, featureClusters = Clust.assignClustersAllFeatures(featureData, clusterParams)
          dateClusters = []
          for icl in range(nclusters):
               dateClusters.append([t for i,t in enumerate(date_list) if classes[i] == icl])
          if actual:
               targetClusters = []
               for icl in range(nclusters):
                    targetClusters.append([t for i,t in enumerate(target) if classes[i] == icl])
     else:
          # everything is one cluster
          classes = range(len(target))
          featureClusters = [featureData]
          dateClusters = [date_list]
          if actual:
               targetClusters = [target]

     preds = []
     RMSE = []
     R2 = []
     for icl in range(nclusters):
          # convert features and target to arrays
          featureClusters[icl] = (np.array(featureClusters[icl])).T

          if scale:
               scaler = scalers[icl]
               featureClusters[icl] = scaler.transform(featureClusters[icl])

          regr = regrs[icl]
          preds.append(regr.predict(featureClusters[icl]))
          if actual:
               targetClusters[icl] = np.array(targetClusters[icl])
               print('Cluster %d, %d rows:' % (icl,len(dateClusters[icl])) )
               r2 = regrs[icl].score(featureClusters[icl],targetClusters[icl])
               print('  R^2_mean:' + '\t' + str(r2))
               rmse = np.sqrt(((preds[icl] - targetClusters[icl])**2).mean())
               print('  RMSE:\t' + '\t' + str(rmse))
               RMSE.append(rmse)
               R2.append(r2)

     # assemble predictions into one list
     date_list_mixed = np.concatenate(dateClusters).tolist()
     pred_mixed = np.concatenate(preds).tolist()
     pred = [pr for (d,pr) in sorted(zip(date_list_mixed,pred_mixed))]

     if actual:
          rmse = np.sqrt(((np.array(pred) - np.array(target))**2).mean()) 
          print('\nOverall performance:')
          print('  RMSE:' + '\t' + str(rmse))

          modelPerf = {'RMSE': RMSE, 'R2': R2, 'RMSE_total': rmse }
     else:
          modelPerf = None

     return date_list, pred, target, featureData, classes, modelPerf


###############################################################
################## MODEL USING PCA ############################
###############################################################
#
def pcaClusterModel(stations, startDate, endDate, \
                   features, ncomp=None, \
                   clusterVars=[], nclusters=1, \
                   targetVar='TempMax', \
                   lag=1, order=0, ranseed=666, verbose=False):
     # build regression model to predict "variable" for a single
     # station using training data from multiple stations 
     # between startdate and enddate.
     #
     # The set of values of each feature at all stations is converted
     # to a truncated list of principal components for purposes of 
     # feature-reduction and reduction of multicolinearity 
     # 
     # Clustering is used to train multiple models for different
     # partitions of the data
     #
     # Uses a "Taylor expansion" by combining information from 
     # several days (higher order time derivatives)
     #
     # stations: a list of station codes, the first entry is
     #             the station for which forecast is generated
     # features: a list of variables to use as predictors
     #    ncomp: a list of same length as features containing the
     #           number of PCA to keep for each feature
     # clusterVars: a list of pairs of form ('feature',npc), where
     #              where npc is the index of the PC to use for
     #              clustering
     #      lag: the number of days in the future to forecast
     #    order: the number of days in the past to include
     #           (also maximum order of time derivative)
     import numpy as np
     import wUUtils as Util
     import wUPCA
     import wUCluster as Clust
     from sklearn import preprocessing
     from sklearn import linear_model
     # load target variable data
     target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                        targetVar, castFloat=True)
     # shift vector by lag
     target = target[lag:]
     # load features data and compute PC
     pcaData, transformParams = wUPCA.pcaConvert(stations, features, \
                                                 startDate, endDate, ncomp)
     # flatten featureData into single list of lists, while shortening by lag
     featureData = [data[:(-lag)] for dataList in pcaData for data in dataList] 
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

     # apply clustering
     # locate columns to be used for clustering
     cols = []
     for clusterPair in clusterVars:
          ifeat = features.index(clusterPair[0]) # index of feature
          col = sum(ncomp[:ifeat]) + clusterPair[1]
          cols += [col]
          if clusterPair[1] >= ncomp[ifeat]:
               print('Requested cluster variable out of range')
               print(clusterPair[0] + ' ' + str(clusterPair[1]) + ' >= ' + str(ncomp[ifeat]))
               return
     print('columns for clustering: ' + str(cols))

     clusterData = np.array([featureData[ii] for ii in cols]).T
     scaler, clusterer = Clust.computeClusters(clusterData, nclusters, ranseed)
     classes = Clust.assignClusters(scaler, clusterer, clusterData)
     clusterParams = { \
               'scaler': scaler, \
               'clusterer': clusterer, \
               'nclusters': nclusters, \
               'ranseed': ranseed, \
               'cols': cols }

     # separate data into clusters
     featureClusters = []
     targetClusters = []
     for icl in range(nclusters):
         # features
         clust = [f for i,f in enumerate(zip(*featureData)) if classes[i]==icl]
         featureClusters.append( map(list,zip(*clust)) )
         # targetVar
         clust = [t for i,t in enumerate(target) if classes[i]==icl]
         targetClusters.append(clust)

     # train separate regression model for each cluster
     regrs = []
     for icl in range(nclusters):
          # convert features and target to arrays
          featureClusters[icl] = (np.array(featureClusters[icl])).T
          targetClusters[icl] = np.array(targetClusters[icl])

          regr = linear_model.LinearRegression()
          regr.fit(featureClusters[icl], targetClusters[icl])
          regrs.append(regr)
          print('Cluster %d, nrows %d, R^2 %f' \
                       % (icl, \
                          len(targetClusters[icl]), \
                          regr.score(featureClusters[icl],targetClusters[icl])) )
          if verbose:
               print("\nCluster " + str(icl))
               print("Regression coefficients:")
               print("  intercept" + ":\t" + str(regr.intercept_))
               column = 0
               for ideriv in range(order+1):
                    print("  " + str(ideriv) + "th derivative:")
                    for ii, feature in enumerate(features):
                         print("    " + feature)
                         for jj in range(ncomp[ii]):
                              print("      PC " + str(jj) + " :\t" + str(regr.coef_[column]))
                              column += 1

     modelParams = {
            'stations': stations, \
            'startDate': startDate, \
            'endDate': endDate, \
            'targetVar': targetVar, \
            'features': features, \
            'clusterVars': clusterVars, \
            'clusterParams': clusterParams, \
            'classes': classes, \
            'regrs': regrs, \
            'lag': lag, \
            'order': order, \
            'transformParams': transformParams}

     return featureData, target, modelParams

#
def pcaClusterPredict(modelParams, startDate, endDate, actual=True):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     import wUUtils as Util
     import wUCluster as Clust
     import wUPCA
     reload(wUPCA)
     # extract city and feature data
     stations = modelParams['stations']
     targetVar = modelParams['targetVar']
     features = modelParams['features']
     regrs = modelParams['regrs']
     lag = modelParams['lag']
     order = modelParams['order']
     transformParams = modelParams['transformParams']
     ncomp = transformParams['ncomp']
     clusterVars = modelParams['clusterVars']
     clusterParams = modelParams['clusterParams']
     nclusters = clusterParams['nclusters']
     cols = clusterParams['cols']
     scaler = clusterParams['scaler']
     clusterer = clusterParams['clusterer']

     # build list of dates in datetime format
     date_list = Util.dateList(startDate, endDate)
     date_list = date_list[(lag+order):]
     # if actual data available
     if actual:
          # load target variable data
          target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                             targetVar, castFloat=True)
          # shift vector by lag
          target = target[lag:]
          target = np.array(target)
     else:
          target = None

     # load features data and compute PC
     pcaData = wUPCA.pcaPredict(transformParams, startDate, endDate)
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

     # assign points (rows) to clusters
     clusterData = np.array([featureData[ii] for ii in cols]).T
     classes = Clust.assignClusters(scaler, clusterer, clusterData)

     # separate data into clusters
     featureClusters = []
     dateClusters = []
     if actual:
          targetClusters = []
     for icl in range(nclusters):
         # features
         clust = [f for i,f in enumerate(zip(*featureData)) if classes[i]==icl]
         featureClusters.append( map(list,zip(*clust)) )
         if actual:
              # targetVar
              clust = [t for i,t in enumerate(target) if classes[i]==icl]
              targetClusters.append(clust)
         # dates
         dateClusters.append([t for i,t in enumerate(date_list) if classes[i] == icl])

     R2 = []
     RMSE = []
     preds = []
     for icl in range(nclusters):
          regr = regrs[icl]
          # convert features and target to arrays
          featureClusters[icl] = (np.array(featureClusters[icl])).T
          # make predictions
          if len(featureClusters[icl]) > 0:
               preds.append(regr.predict(featureClusters[icl]))
          else:
               preds.append([])
          if actual:
               targetClusters[icl] = np.array(targetClusters[icl])
               print('Cluster %d, %d rows:' % (icl,len(dateClusters[icl])) )
               if len(featureClusters[icl]) > 0:
                    r2 = regrs[icl].score(featureClusters[icl],targetClusters[icl])
                    print('  R^2_mean:' + '\t' + str(r2))
                    rmse = np.sqrt(((preds[icl] - targetClusters[icl])**2).mean())
                    print('  RMSE:\t' + '\t' + str(rmse))
                    RMSE.append(rmse)
                    R2.append(r2)
               else:
                    RMSE.append(None)
                    R2.append(None)
     
     # assemble predictions into one list
     date_list_mixed = np.concatenate(dateClusters).tolist()
     pred_mixed = np.concatenate(preds).tolist()
     pred = [pr for (d,pr) in sorted(zip(date_list_mixed,pred_mixed))]

     if actual:
          rmse = np.sqrt(((np.array(pred) - np.array(target))**2).mean()) 
          print('\nOverall performance:')
          print('  RMSE:' + '\t' + str(rmse))

          modelPerf = {'RMSE': RMSE, 'R2': R2, 'RMSE_total': rmse }
     else:
          modelPerf = None

     return date_list, pred, target, featureData, classes, modelPerf

