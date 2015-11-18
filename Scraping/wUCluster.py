################################################################
################## K MEANS CLUSTERING ##########################
################################################################
#
def computeClusters(data, nclusters, ranseed = 666, scale=True):
     # use K means clustering to compute nclusters clusters from
     # a set of training data points
     #
     import numpy as np
     from sklearn import preprocessing
     from sklearn.cluster import KMeans 
     scaler = None
     if scale:
          scaler = preprocessing.StandardScaler().fit(data)
          scaledData = scaler.transform(data)
     else:
          scaledData = data

     clusterer = KMeans(n_clusters = nclusters, random_state = ranseed)
     clusterer.fit(scaledData)

     return scaler, clusterer

#
def assignClusters(scaler, clusterer, data):
     #
     # assign a set of points to one of a set of given clusters
     #
     # clusterer: list of N cluster centres
     #    data: array with N columns
     #
     if scaler == None:
          scaledData = data
     else:
          scaledData = scaler.transform(data)
     classes = clusterer.predict(scaledData)
     return classes

#
def clusterFeatures(featureData, features, clusterFeatures, nclusters):
     # - separate features to be used for clustering
     # - compute clusters
     import numpy as np
     cols = [features.index(f) for f in features if f in clusterFeatures]
     clusterData = np.array([featureData[ii] for ii in cols]).T
     scaler, clusterer = computeClusters(clusterData, nclusters)
     classes = assignClusters(scaler, clusterer, clusterData)
     clusterParams = { \
               'scaler': scaler, \
               'clusterer': clusterer, \
               'nclusters': nclusters, \
               'features': features, \
               'clusterFeatures': clusterFeatures}
     return classes, clusterParams

#
def assignClustersAllFeatures(featureData, clusterParams):
     # separate data into subsets by class
     scaler = clusterParams['scaler']
     clusterer = clusterParams['clusterer']
     features = clusterParams['features']
     clusterFeatures = clusterParams['clusterParams']
     nclusters = clusterParams['nclusters']

     cols = [features.index(f) for f in features if f in clusterFeatures]
     clusterData = np.array([featureData[ii] for ii in cols]).T
     classes = assignClusters(scaler, clusterer, clusterData)

     clusters = []
     for cl in range(nclusters):
          clust = [[f[i] for i,f in enumerate(feat) if classes[i]==cl] \
                         for feat in featureData]
          clusters.append(clust)
     return classes, clusters
