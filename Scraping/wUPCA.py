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


