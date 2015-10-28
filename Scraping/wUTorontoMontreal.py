#          
###############################################################
###################### INTERACTIVE EXAMPLE ####################
###############################################################
#
'''
# In Python terminal session:
import wUnderground
import wUPlots
import wUTorontoMontreal as wUTM
# read data and save in tuple DDD
DDD = wUTM.TorontoMontreal_Winter_2002_2003()
# prepare plots
PPP = wUTM.PreparePlots(*DDD)
# draw example plots
wUTM.DrawPlots(*PPP)
#
#------------------
# make a plot of difference in maximum Temp between Tor and Mtl 
# in December 2002 (by hand)
import matplotlib.pyplot as plt
from numpy import array
plotDate, plotTor, plotMtl = PPP
# find indices corresponding to desired date range
indices = [i for i,x in enumerate(plotDate) \
		if x.isoformat() == '2002-12-01' \
		or x.isoformat() == '2002-12-31']
Tmax_Tor = wUPlots.computeStatistic('TemperatureC','max',plotTor,indices)
Tmax_Mtl = wUPlots.computeStatistic('TemperatureC','max',plotMtl,indices)
december = plotDate[indices[0]:indices[1]+1]
# create figure
fig = plt.figure()
ax = fig.add_subplot(111)
ax.grid(True)
ax.fill_between(december,Tmax_Tor,Tmax_Mtl, \
          where=array(Tmax_Mtl)<=array(Tmax_Tor), \
		interpolate=True, facecolor='wheat')
ax.fill_between(december,Tmax_Tor,Tmax_Mtl, \
          where=array(Tmax_Mtl)>=array(Tmax_Tor), \
		interpolate=True, facecolor='salmon')
pt, = ax.plot(december,Tmax_Tor,color='r',label='Toronto')
pm, = ax.plot(december,Tmax_Mtl,color='b',label='Montreal')
fig.autofmt_xdate()
plt.title('Difference between daily max temp in Toronto and Montreal')
plt.ylabel('Daily max temperature (C)')
plt.legend(handles=[pt,pm])
plt.show()
'''
#
###############################################################
######### TORONTO-MONTREAL RETRIEVAL AND VISUALIZATION ########
###############################################################
#
#--
def DrawPlots(plotDate, plotTor, plotMtl):
	import wUPlots as wUP
	# load matplotlib.pyplot
	import matplotlib.pyplot as plt
	# -- plot ranges of SLP and TempC for Toronto
	wUP.plotDailyRange(plotDate, plotTor, 'Sea Level PressurehPa', \
			'2002-12-21', '2003-03-20', \
			title='Toronto Winter 2002-2003', show=False)
	wUP.plotDailyRange(plotDate, plotTor, 'TemperatureC', \
			'2002-12-21', '2003-03-20', \
			title='Toronto Winter 2002-2003', show=False)
	# compare daily minimum temperature from Toronto and Montreal
	wUP.compareDailyStat(plotDate, [plotTor, plotMtl], 'TemperatureC', \
			'2002-12-21', '2003-03-20', \
			leg = ['Toronto', 'Montreal'], \
			stat='min', \
			title='Winter 2002-2003', \
			show=False)
	# repeat for max wind speed
	wUP.compareDailyStat(plotDate, [plotTor, plotMtl], 'Wind SpeedKm/h', \
			'2002-12-21', '2003-03-20', \
			leg = ['Toronto', 'Montreal'], \
			stat='max', \
			title='Winter 2002-2003', \
			show=False)
	# repeat for min humidity
	wUP.compareDailyStat(plotDate, [plotTor, plotMtl], 'Humidity', \
			'2002-12-21', '2003-03-20', \
			leg = ['Toronto', 'Montreal'], \
			stat='min', \
			title='Winter 2002-2003', \
			show=False)
	plt.show()
#--
def PreparePlots(dates, tor, tor_fails, mtl, mtl_fails):
	# -- remove days missing from one or the other
	fail_indices = [fl[0] for fl in tor_fails] \
			and [fl[0] for fl in mtl_fails]
	plotDate = []; plotTor = []; plotMtl = []
	# -- prepare clean data sets
	for iday in range(len(dates)):
		if iday not in fail_indices:
			plotDate.append(dates[iday])
			plotTor.append(tor[iday])
			plotMtl.append(mtl[iday])
	# make plots
	return plotDate, plotTor, plotMtl
#--
def TorontoMontreal_Winter_2002_2003():
	import wUnderground as wU
	# accumulate data from weather underground
	dates, tor, tor_fails = wU.readInterval('CYYZ','2002-12','2003-03')
	dates, mtl, mtl_fails = wU.readInterval('CYUL','2002-12','2003-03')
	# prepare data for plots (and plot)
	PreparePlots(dates, tor, tor_fails, mtl, mtl_fails)
	# return data
	return dates, tor, tor_fails, mtl, mtl_fails
