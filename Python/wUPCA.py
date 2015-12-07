################################################################
################## PRINCIPAL COMPONENT ANALYSIS ################
################################################################
#
###############################################################
################## PCA DECOMPOSITION ##########################
###############################################################
#
def pcaComp(data, ncomp = None):
     # compute the principal components of a set of vectors
     # defined by the columns of the array data
     # first rescale the data to have zero mean and unit standard deviation
     # return PCA and StandardScaler objects so that new data may
     # be transformed in the same way (e.g. for testing regression model)
     import numpy as np
     from sklearn.decomposition import PCA
     from sklearn import preprocessing
     scaler = preprocessing.StandardScaler().fit(data)
     scaledData = scaler.transform(data)
     if ncomp == None:
          pc = PCA().fit(scaledData)
     else:
          pc = PCA(n_components = ncomp).fit(scaledData)
     return pc, scaler

#
def pcaTransform(pc, scaler, data):
     # scale and transform data using existing transformation
     scaledData = scaler.transform(data)
     pcData = pc.transform(scaledData) 
     return pcData

#
def pcaInverseTransform(pc, scaler, pcData):
     # convert pc data back to original basis
     scaledData = pc.inverse_transform(pcData)
     data = scaler.inverse_transform(scaledData)
     return data

#
def pcaConvert(stations, features, startDate, endDate, ncomp=None):
     # given a set of features at a set of stations,
     #   - for each feature, rescale data and 
     #     compute the leading ncomp principal components
     #   - return the list of values of each pca component
     #   - return a dictionary containing:
     #      - a list of the feature names
     #      - a list of the station names
     #      - the number of pca per feature
     #      - a list of the scaler transforms (one per feature)
     #      - a list of the pca transform (one per feature)
     import numpy as np
     import wUUtils as Util
     scalers = []
     pcas = []
     pcaData = []
     if ncomp == None:
          nc = len(features)*[len(stations)]
     else:
          nc = ncomp
     for ifeat, feature in enumerate(features):
          data = []
          for station in stations:
               vals = Util.loadDailyVariableRange( \
                             station, startDate, endDate, \
                             feature, castFloat=True)
               data.append(vals)
          # convert data to a numpy array with features as columns
          data = np.array(data).T
          # compute pca transform and standardization transform
          pc, scaler = pcaComp(data, nc[ifeat])
          # transform data to standardized pca space
          pcaData1 = pcaTransform(pc, scaler, data)
          # convert to a list of principal components
          pcaData1 = (pcaData1.T).tolist()

          # add transforms and principal components to corresponding lists
          scalers.append(scaler)
          pcas.append(pc)
          pcaData.append(pcaData1)

     transform_params = { \
          'features': features, \
          'stations': stations, \
          'ncomp': nc, \
          'scalers': scalers, \
          'pcas': pcas }
     return pcaData, transform_params

#
def pcaPredict(transform_params, startDate, endDate):
     # apply pca and scaling transform constructed on a training
     # set to an out-of-sample (or in-sample!) set
     import numpy as np
     import wUUtils as Util
     stations = transform_params['stations']
     features = transform_params['features']
     scalers = transform_params['scalers']
     pcas = transform_params['pcas']

     pcaData = []
     for ifeat, feature in enumerate(features):
          data = []
          for station in stations:
               vals = Util.loadDailyVariableRange( \
                             station, startDate, endDate, \
                             feature, castFloat=True)
               data.append(vals)
          # convert data to a numpy array with features as columns
          data = np.array(data).T
          # transform data to standardized pca space
          pcaData1 = pcaTransform(pcas[ifeat], scalers[ifeat], data)
          # convert to a list of principal components
          pcaData1 = (pcaData1.T).tolist()
          # add pc data to list
          pcaData.append(pcaData1)
     return pcaData

###############################################################
################## PCA DECOMPOSITION IF DATA ALREADY SAVED ####
###############################################################
#
#
def pcaConvertOnly(featureData, nstations, ncomp=None):
     # given a set of featureData (!) at a set of stations,
     #   - for each feature, rescale data and 
     #     compute the leading ncomp principal components
     #   - return the list of values of each pca component
     #   - return a dictionary containing:
     #      - a list of the feature names
     #      - a list of the station names
     #      - the number of pca per feature
     #      - a list of the scaler transforms (one per feature)
     #      - a list of the pca transform (one per feature)
     import numpy as np
     import wUUtils as Util
     scalers = []
     pcas = []
     pcaData = []
     nfeatures = len(featureData)/nstations
     if ncomp == None:    # compute all PC for each feature
          nc = nfeatures*[nstations]
     else:
          nc = ncomp
     for ifeat in range(nfeatures):
          start = ifeat*nstations
          finish = (ifeat+1)*nstations
          data = featureData[start:finish]
          # convert data to a numpy array with features as columns
          data = np.array(data).T
          # compute pca transform and standardization transform
          pc, scaler = pcaComp(data, nc[ifeat])
          # transform data to standardized pca space
          pcaData1 = pcaTransform(pc, scaler, data)
          # convert to a list of principal components
          pcaData1 = (pcaData1.T).tolist()

          # add transforms and principal components to corresponding lists
          scalers.append(scaler)
          pcas.append(pc)
          pcaData.append(pcaData1)

     transform_params = { \
          'nstations': nstations, \
          'nfeatures': nfeatures, \
          'ncomp': nc, \
          'scalers': scalers, \
          'pcas': pcas }
     return pcaData, transform_params

#
def pcaPredictOnly(featureData, transform_params):
     # apply pca and scaling transform constructed on a training
     # set to an out-of-sample (or in-sample!) set
     import numpy as np
     import wUUtils as Util
     nstations = transform_params['nstations']
     nfeatures = transform_params['nfeatures']
     scalers = transform_params['scalers']
     pcas = transform_params['pcas']

     pcaData = []
     for ifeat in range(nfeatures):
          start = ifeat*nstations
          finish = (ifeat+1)*nstations
          data = featureData[start:finish]
          # convert data to a numpy array with features as columns
          data = np.array(data).T
          # transform data to standardized pca space
          pcaData1 = pcaTransform(pcas[ifeat], scalers[ifeat], data)
          # convert to a list of principal components
          pcaData1 = (pcaData1.T).tolist()
          # add pc data to list
          pcaData.append(pcaData1)
     return pcaData

