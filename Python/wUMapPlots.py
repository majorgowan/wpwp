###############################################################
################## PLOTS ON MAP BACKGROUND ####################
###############################################################
#
# ref: http://matplotlib.org/basemap/users/geography.html

###############################################################
################# PLOT POINTS AND LABELS ON MAP ###############
###############################################################
#
def plotStationsOnMap(showIt=True):
     import wUUtils as Util
     from mpl_toolkits.basemap import Basemap
     import matplotlib.pyplot as plt
     # setup Lambert Conformal basemap.
     m = Basemap(width=3200000,height=2500000,projection='lcc',
            resolution='i',lat_1=45.,lat_0=43.6,lon_0=-81.)
     # draw coastlines.
     m.drawcoastlines(color='gray')
     m.drawcountries(color='gray')
     m.drawstates(color='gray')
     # draw a boundary around the map, fill the background.
     # this background will end up being the ocean color, since
     # the continents will be drawn on top.
     m.drawmapboundary(fill_color='lightblue')
     # fill continents, set lake color same as ocean color.
     m.fillcontinents(color='navajowhite',lake_color='lightblue')
     # plot city locations
     cityName = Util.getStationList()
     lon, lat = Util.getStationLonLat(cityName)
     # convert to map projection coords.
     # Note that lon,lat can be scalars, lists or numpy arrays.
     xpt,ypt = m(lon,lat)
     m.plot(xpt,ypt,'bo')  # plot a blue dot there
     for icity, city in enumerate(cityName):
          if city == 'KBUF':
               xoff, yoff = 20000, -40000
          elif city == 'CYOW':
               xoff, yoff = -100000, 23000
          else:
               xoff, yoff = 20000, 20000
          plt.text(xpt[icity]+xoff,ypt[icity]+yoff, \
                   city, \
                   fontweight='bold', \
                   fontsize='medium', \
                   color='navy')
     if showIt:
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
def plotAdvectionOnMap(targetStation, variable, date, \
                       width_fac = 16, height_fac = 12):
     from mpl_toolkits.basemap import Basemap
     import matplotlib.pyplot as plt
     import wUAdvection as Adv
     import wUUtils as Util
     # setup Lambert Conformal basemap.
     m = Basemap(width=width_fac*100000,height=height_fac*100000, \
                 projection='lcc', resolution='i', \
                 lat_1=45.,lat_0=43.6,lon_0=-82.)
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
     # get station locations (Toronto, Montreal, Detroit)
     stations = Util.getStationList()
     lon, lat = Util.getStationLonLat(stations)
     # convert to map projection coords.
     # Note that lon,lat can be scalars, lists or numpy arrays.
     xpt,ypt = m(lon,lat)
     m.plot(xpt,ypt,'bo')  # plot a blue dot there
     # compute advection arrows between all other cities
     # and the target station
     for istation in range(len(stations)):
          if stations[istation] != targetStation:
               # print(targetStation, stations[istation], variable, date, date)
               dD, uVec = Adv.dDeriv(targetStation, stations[istation], variable, \
                       date, nextDay(date))
               stretch = 2500
               dD = stretch*dD[0]
               dx, dy = dD*uVec
               plt.arrow(xpt[istation],ypt[istation],dx,dy,color='r',width=12000,head_length=40000,head_width=40000)
     for istation in range(len(stations)):
          plt.text(xpt[istation]+30000,ypt[istation]+20000,stations[istation])
     plt.show()

#
def plotWindVectorsOnMap(date, showIt=True):
     from mpl_toolkits.basemap import Basemap
     import matplotlib.pyplot as plt
     import wUUtils as Util
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
     cityName = Util.getStationList()
     lon, lat = Util.getStationLonLat(cityName)
     # convert to map projection coords.
     # Note that lon,lat can be scalars, lists or numpy arrays.
     xpt,ypt = m(lon,lat)
     m.plot(xpt,ypt,'bo')  # plot a blue dot there
     # compute wind vectors
     windX = Util.loadDailyVariable(cityName, date, 'WindMeanX')
     windY = Util.loadDailyVariable(cityName, date, 'WindMeanY')
     for icity in range(len(cityName)):
          stretch = 20000
          dx, dy = stretch*windX[icity], stretch*windY[icity]
          plt.arrow(xpt[icity],ypt[icity],dx,dy,color='r',width=12000,head_length=40000,head_width=40000)
          plt.text(xpt[icity]+30000,ypt[icity]+20000,cityName[icity], size='large')
     plt.title("Daily-mean wind: " + date)
     if showIt:
          plt.show()

#
def plotMeanWindVectorsOnMap(startDate, endDate, showIt=True):
     import numpy as np
     import wUUtils as Util
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
     # get station locations (Toronto, Montreal, Detroit)
     stations = Util.getStationList()
     lon, lat = Util.getStationLonLat(stations)
     # convert to map projection coords.
     # Note that lon,lat can be scalars, lists or numpy arrays.
     xpt,ypt = m(lon,lat)
     m.plot(xpt,ypt,'bo')  # plot a blue dot there
     # calculate mean wind at each station
     windX = []
     windY = []
     for station in stations:
          wX = Util.loadDailyVariableRange(station, startDate, endDate, \
                                        'WindMeanX', castFloat=True)
          windX.append(np.mean(wX))
          wY = Util.loadDailyVariableRange(station, startDate, endDate, \
                                        'WindMeanY', castFloat=True)
          windY.append(np.mean(wY))
     for istation in range(len(stations)):
          stretch = 50000
          dx, dy = stretch*windX[istation], stretch*windY[istation]
          plt.arrow(xpt[istation],ypt[istation],dx,dy,color='r',width=12000,head_length=40000,head_width=40000)
          plt.text(xpt[istation]+30000,ypt[istation]+20000,stations[istation], size='large')
     plt.title("Time-mean Wind: " + startDate + " to " + endDate)
     if showIt:
          plt.show()


###############################################################
################# CONTOUR PLOTS OF DATA ON MAP BACKGROUND #####
###############################################################
#
def contourPlot(lon, lat, data, title='data'):
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
     plt.colorbar(orientation='horizontal')
     plt.title(title)
     plt.show()
     
#
def contourPlotOnMap(lon, lat, data, title='data', \
                     width_fac = 16, height_fac = 12, showIt=True):
     import numpy as np
     import matplotlib.pyplot as plt
     import scipy.interpolate

     from mpl_toolkits.basemap import Basemap

     # compute centre of lon/lat set
     lon0, lat0 = 0.5*(np.min(lon)+np.max(lon)), \
                  0.5*(np.min(lat)+np.max(lat))
     # print('centre at: ', lon0, lat0)
     # open new figure window
     plt.figure()
     # setup Lambert Conformal basemap.
     m = Basemap(width=width_fac*100000,height=height_fac*100000, \
                 projection='lcc', resolution='i', \
                 lat_1=45.,lat_0=lat0,lon_0=lon0)
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
     plt.title(title)
     if showIt:
          # display plot
          plt.show()

#
def contourPlotStationsOnMap(stations, data, title='data', \
                             width_fac = 16, height_fac = 12):
     import wUUtils as Util
     lon, lat = Util.getStationLonLat(stations)
     contourPlotOnMap(lon, lat, data, title, width_fac, height_fac)

#
def contourPlotVarOnMap(variable, date, npts = 20, ncntrs = 10, \
                            width_fac = 16, height_fac = 12):
     import numpy as np
     import wUUtils as Util
     import matplotlib.pyplot as plt
     import scipy.interpolate
     from mpl_toolkits.basemap import Basemap
     # open new figure window
     plt.figure()
     # setup Lambert Conformal basemap.
     m = Basemap(width=width_fac*100000,height=height_fac*100000, \
                 projection='lcc', resolution='i', \
                 lat_1=45.,lat_0=43.6,lon_0=-82.)
     # draw coastlines.
     m.drawcoastlines()
     m.drawcountries()
     m.drawstates()
     # draw a boundary around the map, fill the background.
     # this background will end up being the ocean color, since
     # the continents/data will be drawn on top.
     m.drawmapboundary(fill_color='aqua')
     # load data
     stations = Util.getStationList()
     lon, lat = Util.getStationLonLat(stations)
     data = Util.loadDailyVariable(stations, date, variable)
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

#
def contourPlotMeanVarOnMap(variable, startDate, endDate, \
                            npts = 20, ncntrs = 10, \
                            width_fac = 16, height_fac = 12):
     import numpy as np
     import wUUtils as Util
     import matplotlib.pyplot as plt
     import scipy.interpolate
     from mpl_toolkits.basemap import Basemap
     # open new figure window
     plt.figure()
     # setup Lambert Conformal basemap.
     m = Basemap(width=width_fac*100000,height=height_fac*100000, \
                 projection='lcc', resolution='i', \
                 lat_1=45.,lat_0=43.6,lon_0=-82.)
     # draw coastlines.
     m.drawcoastlines()
     m.drawcountries()
     m.drawstates()
     # draw a boundary around the map, fill the background.
     # this background will end up being the ocean color, since
     # the continents/data will be drawn on top.
     m.drawmapboundary(fill_color='aqua')
     # load data
     stations = Util.getStationList()
     lon, lat = Util.getStationLonLat(stations)
     data = []
     for station in stations:
          vals = Util.loadDailyVariableRange(station, startDate, endDate, \
                                        variable, castFloat=True)
          data.append(np.mean(vals))
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
     plt.title(variable + " -- Mean " + startDate + " to " + endDate)
     # display plot
     plt.show()
     
