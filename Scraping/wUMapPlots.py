###############################################################
################## PLOTS ON MAP BACKGROUND ####################
###############################################################
#
# ref: http://matplotlib.org/basemap/users/geography.html
     
###############################################################
################# LOAD DATA FOR ALL CITIES ####################
###############################################################
#
def getStationList():
     import glob
     stations = []
     for infile in glob.glob('CSV_DATA/*'):
         stations.append(infile.split('\\')[1].split('.')[0])
     return stations

def getStationLonLat(stations):
     # data from http://ourairports.com/data/
     # identifier in column 1 (0-based), lat-lon in columns 4,5
     lon = []
     lat = []
     for station in stations:
          with open('AIRPORT_DATA/airports.csv') as airportfile:
               for nline in airportfile:
                    nlist = nline.split(',')
                    if station in nlist[1]:
                        lon.append(float(nlist[5]))
                        lat.append(float(nlist[4]))
                        break
     return lon, lat               
     
#
def loadDailyVariable(stations, outdate, variable):
     vals = []
     for station in stations:
          with open('CSV_DATA/' + station + '.csv','r') as infile:
               header = infile.readline().strip().split(', ')
               datepos = header.index('date')
               varpos = header.index(variable)
               for nline in infile:
                    nlist = nline.strip().split(', ')
                    nday = nlist[datepos]
                    if nday == outdate:
                         vals.append(float(nlist[varpos]))
                         break
     return vals          

###############################################################
################# PLOT POINTS AND LABELS ON MAP ###############
###############################################################
#
def plotOnMap():
     from mpl_toolkits.basemap import Basemap
     import matplotlib.pyplot as plt
     # setup Lambert Conformal basemap.
     m = Basemap(width=3200000,height=2500000,projection='lcc',
            resolution='i',lat_1=45.,lat_0=43.6,lon_0=-80.)
     # draw coastlines.
     m.drawcoastlines()
     m.drawcountries()
     m.drawstates()
     # draw a boundary around the map, fill the background.
     # this background will end up being the ocean color, since
     # the continents will be drawn on top.
     m.drawmapboundary(fill_color='aqua')
     # fill continents, set lake color same as ocean color.
     m.fillcontinents(color='wheat',lake_color='aqua')
     # plot city locations (Toronto, Montreal, Detroit)
     cityName = getStationList()
     lon, lat = getStationLonLat(cityName)
#     lon, lat = -79.6306, 43.6767 # Location of Boulder
     # convert to map projection coords.
     # Note that lon,lat can be scalars, lists or numpy arrays.
     xpt,ypt = m(lon,lat)
     m.plot(xpt,ypt,'bo')  # plot a blue dot there
     for icity in range(len(cityName)):
          plt.text(xpt[icity]+30000,ypt[icity]+20000,cityName[icity])
     plt.show()

###############################################################
################# ADVECTION ARROWS ON MAP #####################
###############################################################
#
def nextDay(date):
     # horrible hack to make advection plot need only one date
     import datetime
     day0 = datetime.datetime.strptime(date,"%Y-%m-%d") + datetime.timedelta(days=1)
     return day0.date().isoformat()

#
def plotAdvectionOnMap(targetStation, variable, date):
     from mpl_toolkits.basemap import Basemap
     import matplotlib.pyplot as plt
     import wUAdvection as Adv
     # setup Lambert Conformal basemap.
     m = Basemap(width=3200000,height=2500000,projection='lcc',
            resolution='i',lat_1=45.,lat_0=43.6,lon_0=-80.)
     # draw coastlines.
     m.drawcoastlines()
     m.drawcountries()
     m.drawstates()
     # draw a boundary around the map, fill the background.
     # this background will end up being the ocean color, since
     # the continents will be drawn on top.
     m.drawmapboundary(fill_color='aqua')
     # fill continents, set lake color same as ocean color.
     m.fillcontinents(color='wheat',lake_color='aqua')
     # get city locations (Toronto, Montreal, Detroit)
     cityName = getStationList()
     lon, lat = getStationLonLat(cityName)
     # convert to map projection coords.
     # Note that lon,lat can be scalars, lists or numpy arrays.
     xpt,ypt = m(lon,lat)
     m.plot(xpt,ypt,'bo')  # plot a blue dot there
     # compute advection arrows between all other cities
     # and the target city
     for icity in range(len(cityName)):
          if cityName[icity] != targetStation:
               # print(targetStation, cityName[icity], variable, date, date)
               dD, uVec = Adv.dDeriv(targetStation, cityName[icity], variable, \
                       date, nextDay(date))
               dD = 2000*dD[0]
               dx, dy = dD*uVec
               #print(cityName[icity], dD, uVec)
               plt.arrow(xpt[icity],ypt[icity],dx,dy,color='r')
     for icity in range(len(cityName)):
          plt.text(xpt[icity]+30000,ypt[icity]+20000,cityName[icity])
     plt.show()

#
def plotWindVectorsOnMap(date):
     from mpl_toolkits.basemap import Basemap
     import matplotlib.pyplot as plt
     # setup Lambert Conformal basemap.
     m = Basemap(width=3200000,height=2500000,projection='lcc',
            resolution='i',lat_1=45.,lat_0=43.6,lon_0=-80.)
     # draw coastlines.
     m.drawcoastlines()
     m.drawcountries()
     m.drawstates()
     # draw a boundary around the map, fill the background.
     # this background will end up being the ocean color, since
     # the continents will be drawn on top.
     m.drawmapboundary(fill_color='aqua')
     # fill continents, set lake color same as ocean color.
     m.fillcontinents(color='wheat',lake_color='aqua')
     # get city locations (Toronto, Montreal, Detroit)
     cityName = getStationList()
     lon, lat = getStationLonLat(cityName)
     # convert to map projection coords.
     # Note that lon,lat can be scalars, lists or numpy arrays.
     xpt,ypt = m(lon,lat)
     m.plot(xpt,ypt,'bo')  # plot a blue dot there
     # compute wind vectors
     windX = loadDailyVariable(cityName, date, 'WindMeanX')
     windY = loadDailyVariable(cityName, date, 'WindMeanY')
     for icity in range(len(cityName)):
          stretch = 20000
          dx, dy = stretch*windX[icity], stretch*windY[icity]
          plt.arrow(xpt[icity],ypt[icity],dx,dy,color='r',width=8000,head_length=30000,head_width=20000)
          plt.text(xpt[icity]+30000,ypt[icity]+20000,cityName[icity], size='large')
     plt.show()


###############################################################
################# CONTOUR PLOTS OF DATA ON MAP BACKGROUND #####
###############################################################
#
def contourPlot(lon, lat, data):
     # based on http://stackoverflow.com/questions/9008370/python-2d-contour-plot-from-3-lists-x-y-and-rho
     import numpy as np
     import matplotlib.pyplot as plt
     import scipy.interpolate
     # convert data to arrays:
     x, y, z = np.array(lon), np.array(lat), np.array(data)
     # Set up a regular grid of interpolation points
     xi, yi = np.linspace(x.min(), x.max(), 20), \
              np.linspace(y.min(), y.max(), 20)
     xi, yi = np.meshgrid(xi, yi)
     # Interpolate
     rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
     zi = rbf(xi, yi)
     # colour contour plot with gradients
     plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower',
                extent=[x.min(), x.max(), y.min(), y.max()])
     # simple contour plot:
     # plt.contour(xi, yi, zi)
     # plot points
     plt.scatter(x, y, c=z)
     plt.colorbar()
     plt.show()
     
#
def contourPlotOnMap(lon, lat, data):
     import numpy as np
     import matplotlib.pyplot as plt
     import scipy.interpolate

     from mpl_toolkits.basemap import Basemap
     # open new figure window
     plt.figure()
     # setup Lambert Conformal basemap.
     m = Basemap(width=1700000,height=1400000,projection='lcc',
            resolution='i',lat_1=45.,lat_0=43.6,lon_0=-82.)
     # draw coastlines.
     m.drawcoastlines()
     m.drawcountries()
     m.drawstates()
     # draw a boundary around the map, fill the background.
     # this background will end up being the ocean color, since
     # the continents/data will be drawn on top.
     m.drawmapboundary(fill_color='aqua')
     # convert data to arrays:
     x, y, z = np.array(lon), np.array(lat), np.array(data)
     # map data points to projection coordinates
     xmap, ymap = m(x,y)
     # Set up a regular grid of interpolation points
     xi, yi = np.linspace(x.min(), x.max(), 30), \
              np.linspace(y.min(), y.max(), 30)
     # map regular lon-lat grid to projection coordinates
     xi, yi = m(*np.meshgrid(xi,yi))
     # Interpolate data to projected regular grid (change linear ...)
     rbf = scipy.interpolate.Rbf(xmap, ymap, z, function='linear')
     zi = rbf(xi, yi)
     # draw filled contours
     cs = m.contourf(xi,yi,zi,20,cmap=plt.cm.jet)
     # plot circles at original (projected) data points
     m.scatter(xmap,ymap,c=z)  
     # add colorbar.
     cbar = m.colorbar(cs,location='bottom',pad="5%")
     cbar.set_label('data')
     # display plot
     plt.show()

#
def contourPlotStationsOnMap(stations, data):
     lon, lat = getStationLonLat(stations)
     contourPlotOnMap(lon, lat, data)

#
def contourPlotVarOnMap(variable, date, npts = 20, ncntrs = 10):
     import numpy as np
     import matplotlib.pyplot as plt
     import scipy.interpolate
     from mpl_toolkits.basemap import Basemap
     # open new figure window
     plt.figure()
     # setup Lambert Conformal basemap.
     m = Basemap(width=1600000,height=1200000,projection='lcc',
            resolution='i',lat_1=45.,lat_0=43.6,lon_0=-82.)
     # draw coastlines.
     m.drawcoastlines()
     m.drawcountries()
     m.drawstates()
     # draw a boundary around the map, fill the background.
     # this background will end up being the ocean color, since
     # the continents/data will be drawn on top.
     m.drawmapboundary(fill_color='aqua')
     # load data
     stations = getStationList()
     lon, lat = getStationLonLat(stations)
     data = loadDailyVariable(stations, date, variable)
     # print(zip(stations,data))
     # convert data to arrays:
     x, y, z = np.array(lon), np.array(lat), np.array(data)
     # map data points to projection coordinates
     xmap, ymap = m(x,y)
     # Set up a regular grid of interpolation points
     xi, yi = np.linspace(x.min(), x.max(), npts), \
              np.linspace(y.min(), y.max(), npts)
     # map regular lon-lat grid to projection coordinates
     xi, yi = m(*np.meshgrid(xi,yi))
     # Interpolate data to projected regular grid 
     # function is one of 'linear', 'multiquadric', 'gaussian',
     #                    'inverse', 'cubic', 'quintic', 'thin_plate'
     rbf = scipy.interpolate.Rbf(xmap, ymap, z, \
                                 function='linear')
     zi = rbf(xi, yi)
     # draw filled contours
     cs = m.contourf(xi,yi,zi,ncntrs,cmap=plt.cm.jet)
     # plot circles at original (projected) data points
     m.scatter(xmap,ymap,c=z)  
     # add colorbar.
     cbar = m.colorbar(cs,location='bottom',pad="5%")
     cbar.set_label(variable)
     plt.title(variable + " -- " + date)
     # display plot
     plt.show()
