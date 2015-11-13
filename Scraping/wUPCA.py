################################################################
################## PRINCIPAL COMPONENT ANALYSIS ################
################################################################
#
###############################################################
################## PCA DECOMPOSITION ##########################
###############################################################
#
def pcaComp(data):
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
     pc = PCA().fit(scaledData)
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
     import wURegression as Reg
     scalers = []
     pcas = []
     pcaData = []
     for feature in features:
	  data = []
	  for station in stations:
               vals = Reg.loadDailyVariableRange( \
	                         station, startDate, endDate, \
                                 feature, castFloat=True)
	       data.append(vals)
	  # convert data to a numpy array with features as columns
	  data = np.array(data).T
	  # compute pca transform and standardization transform
          pc, scaler = pcaComp(data)
	  # transform data to standardized pca space
          pcaData1 = pcaTransform(pc, scaler, data)
	  # convert to a list of principal components
	  pcaData1 = (pcaData1.T).tolist()

	  # add transforms and principal components to corresponding lists
          scalers.append(scaler)
          pcas.append(pc)
          pcaData.append(pcaData1)

     transform_params = { \
          'features': features,
	  'stations': stations,
	  'ncomp': ncomp,
	  'scalers': scalers,
	  'pcas': pcas }
     return pcaData, transform_params
