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
