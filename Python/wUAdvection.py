################################################################
################## COMPUTE DIRECTIONAL DERIVATIVE ##############
#################### OF A VARIABLE IN DIRECTION ################
################ FROM SOURCE STATION TO TARGET STATION #########
################################################################
#
def unitVector(lon, lat):
     # compute unit vector in direction from station1 to station2
     # returns 2-component numpy array
     import numpy as np
     lonlat1 = np.array([lon[0], lat[0]])
     lonlat2 = np.array([lon[1], lat[1]])
     diff = lonlat2 - lonlat1
     return diff / np.linalg.norm(diff)

###############################################################
################## DIRECTIONAL DERIVATIVE #####################
###############################################################
#
def dDeriv(station1, station2, variable, startDate, endDate):
     # compute directional derivative using
     # (unitVector . windX2, windY2) (var1 - var2)
     import numpy as np
     import wUUtils as Util
     # load longitude and latitude of both stations
     lon, lat = Util.getStationLonLat([station1, station2])
     # compute unit vector from station2 to station1
     uVec = unitVector(lon, lat)
     # print("unit vector: " + str(uVec))
     # get mean wind vector at station2:
     windX2 = Util.loadDailyVariableRange(station2, startDate, endDate, \
                        'WindMeanX', castFloat=True)
     windY2 = Util.loadDailyVariableRange(station2, startDate, endDate, \
                        'WindMeanY', castFloat=True)
     # get variable at station1 and station2
     var1 = Util.loadDailyVariableRange(station1, startDate, endDate, \
                        variable, castFloat=True)
     var2 = Util.loadDailyVariableRange(station2, startDate, endDate, \
                        variable, castFloat=True)
     # construct wind vectors (N x 2 array)
     windVec = np.vstack((windX2, windY2))
     # project wind vector onto unit vector
     proj = np.dot(uVec, windVec)
     dD = (np.array(var1) - np.array(var2)) * proj
     return dD, uVec


