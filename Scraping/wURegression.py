###############################################################
################## REGRESSION MODEL ###########################
###############################################################
#

#
def loadDailyVariableRange(station, startdate, enddate, \
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
               if nday == startdate:
                    recording = True
               if recording:
                    if castFloat:
                         vals.append(float(nlist[varpos]))
                    else:
                         vals.append(nlist[varpos])
               if nday == enddate:
                    recording = False
                    break
     return vals

#
def oneCityModel(station, startdate, enddate, \
                 features, targetVar='TempMax', lag=1):
     # build regression model to predict "variable" for a single
     # station using training data from only the same station 
     # between startdate and enddate
     # features is a list of variables to use as predictors
     import wUStats as Stats
     import numpy as np
     from sklearn import linear_model
     # load target variable data
     target = loadDailyVariableRange(station, startdate, enddate, \
                        targetVar, castFloat=True) 
     # load feature data
     for feature in features:
          print(feature)
'''              
regr = linear_model.LinearRegression()
targ = Reg.loadDailyVariableRange('CYYZ', '2006-01-01', '2010-12-31', 'TempMax', castFloat=True)
torMin = Reg.loadDailyVariableRange('CYYZ', '2006-01-01', '2010-12-31', 'TempMin', castFloat=True)
torMax = Reg.loadDailyVariableRange('CYYZ', '2006-01-01', '2010-12-31', 'TempMax', castFloat=True)
torHum = Reg.loadDailyVariableRange('CYYZ', '2006-01-01', '2010-12-31', 'HumidityMean', castFloat=True)
torPressMax = Reg.loadDailyVariableRange('CYYZ', '2006-01-01', '2010-12-31', 'PressMax', castFloat=True)
torPressMin = Reg.loadDailyVariableRange('CYYZ', '2006-01-01', '2010-12-31', 'PressMin', castFloat=True)
targ = torMax[1:]
targ = np.array(torMax[1:])
v1 = np.array(torMax[:-1])
ft_Tmax = np.array(torMax[:-1])
ft_Tmin = np.array(torMin[:-1])
ft_Pmin = np.array(torPressMin[:-1])
ft_Pmax = np.array(torPressMax[:-1])
ft_Hum = np.array(torHum[:-1])
regr = linear_model.LinearRegression()
help(regr.fit)
feat = np.vstack(ft_Tmax,ft_Tmin,ft_Pmax,ft_Pmin,ft_Hum).T
feat = np.vstack((ft_Tmax,ft_Tmin,ft_Pmax,ft_Pmin,ft_Hum)).T
size(feat)
np.size(feat)
feat.size
feat.shape
regr.fit(feat, targ)
print('Coefficients: \n', regr.coef_)
import matplotlib.pyplot as plt
pred = regr.predict(feat)
plt.scatter(feat, targ,  color='black')
plt.scatter(range(len(targ)), targ,  color='black')
plt.scatter(range(len(targ)), pred,  color='red')
plt.scatter(range(len(targ)), targ,  color='black')
plt.plot(range(len(targ)), pred,  color='red')
ff = array()
ff = np.array()
ff = np.array([])
ff = np.vstack(ff,ft_Hum).T
ff = np.vstack((ff,ft_Hum)).T
ff = np.vstack((ft_Hum)).T
ff = np.vstack((ft_Hum,ft_Hum)).T
'''