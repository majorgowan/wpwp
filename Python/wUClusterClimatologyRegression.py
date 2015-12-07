###############################################################
################## MODEL USING PCA ############################
###############################################################
#
def pcaClusterModel(stations, startDate, endDate, \
                   features, ncomp=None, \
                   clusterVars=[], nclusters=1, \
                   targetVar='TempMax', \
                   smoothWindow=5, \
                   lag=1, order=0, ranseed=666, verbose=False):
     #
     # ******** instead of raw data, first subtract "climatology" from
     # ******** all features and then proceed as usual
     #
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
     import wUPCA as PCA
     reload(PCA)
     import wUCluster as Clust
     import wUClimatology as Climatology
     reload(Climatology)
     from sklearn import preprocessing
     from sklearn import linear_model
     # make date list 
     date_list = Util.dateList(startDate, endDate)
     # load target variable
     target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                        targetVar, castFloat=True)
     # compute climatology for target variable
     climatologyTarget = Climatology.makeClimatologies(stations, startDate, endDate, \
                                                       [targetVar], smoothWindow)
     climatologyTarget = climatologyTarget[0]
     # subtract climatology from target variable to get dependent variable
     target = Climatology.subtractClimatology(target, date_list, climatologyTarget)
     # shift target by lag
     target = target[lag:]

     # load feature data
     featureData = []
     for station in stations:
          for feature in features:
               # print("Adding " + feature + " from " + station)
               fd = Util.loadDailyVariableRange(station, startDate, endDate, \
                             feature, castFloat=True)
               featureData.append(fd)
     # compute climatologies for features
     climatologyFeatures = Climatology.makeClimatologies(stations, startDate, endDate, \
                                                         features, smoothWindow)
     # subtract climatologies from data
     featureData = [Climatology.subtractClimatology(fd, date_list, climatologyFeatures[i/len(stations)]) \
                     for i, fd in enumerate(featureData)]
     # compute PC of featureData
     pcaData, transformParams = PCA.pcaConvertOnly(featureData, len(stations), ncomp)
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
            'transformParams': transformParams, \
            'climatologyTarget': climatologyTarget, \
            'climatologyFeatures': climatologyFeatures}

     return featureData, target, modelParams

#
def pcaClusterPredict(modelParams, startDate, endDate, actual=True, absolute=False):
     # predict targetVar for a single station using 
     # previously generated regression model
     import numpy as np
     import wUUtils as Util
     import wUCluster as Clust
     import wUPCA as PCA
     reload(PCA)
     import wUClimatology as Climatology
     reload(Climatology)
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

     climatologyTarget = modelParams['climatologyTarget']
     climatologyFeatures = modelParams['climatologyFeatures']

     # build list of dates in datetime format
     date_list = Util.dateList(startDate, endDate)

     # if actual data available
     if actual:
          # load target variable data
          target = Util.loadDailyVariableRange(stations[0], startDate, endDate, \
                             targetVar, castFloat=True)
          # subtract climatology from target variable to get dependent variable
          target = Climatology.subtractClimatology(target, date_list, climatologyTarget)
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
               featureData.append(fd)
     # subtract climatologies from data
     featureData = [Climatology.subtractClimatology(fd, date_list, climatologyFeatures[i/len(stations)]) \
                     for i, fd in enumerate(featureData)]
     # compute PC of featureData
     pcaData = PCA.pcaPredictOnly(featureData, transformParams)
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
     
     # shorten date_list (line it up with target)
     date_list = date_list[(lag+order):]

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
     
     if absolute:
          # return predictions and target with climatology added back
          target = Climatology.addClimatology(target, date_list, climatologyTarget)
          pred = Climatology.addClimatology(pred, date_list, climatologyTarget)

     return date_list, pred, target, featureData, classes, modelPerf

