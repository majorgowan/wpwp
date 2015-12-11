###############################################################
################## PLOTS ON MAP BACKGROUND ####################
###############################################################
#
# ref: http://matplotlib.org/basemap/users/geography.html

###############################################################
################# CONTOUR PLOTS OF DATA ON MAP BACKGROUND #####
###############################################################
#
def contourPlotDataOnMapFrame(data, contours, npts = 20, \
                        figname='figure', frameNum=0, \
                        title='Data', units='units', \
                        width_fac = 16, height_fac = 12):
     import numpy as np
     import wUUtils as Util
     import matplotlib.pyplot as plt
     import scipy.interpolate
     from mpl_toolkits.basemap import Basemap
     # open new figure window
     plt.figure()
     # get station locations
     lon, lat = Util.getStationLonLat(Util.getStationList())
     # compute centre of lon/lat set
     lon0, lat0 = 0.5*(np.min(lon)+np.max(lon)), \
                  0.5*(np.min(lat)+np.max(lat))
     # print('centre at: ', lon0, lat0)
     # open new figure window
     fig = plt.figure()
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
     # load data
     stations = Util.getStationList()
     lon, lat = Util.getStationLonLat(stations)
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
     cs = m.contourf(xi,yi,zi,levels=contours,cmap=plt.cm.jet)
     # plot circles at original (projected) data points
     m.scatter(xmap,ymap,c=z)  
     # add colorbar.
     cbar = m.colorbar(cs,location='bottom',pad="5%")
     cbar.set_label(units)
     plt.title(title)
     # save plot
     filename = '%s_frame_%03d.png' % (figname, frameNum)
     # print('saving file: ' + filename)
     plt.savefig(filename, bbox_inches='tight')
     plt.close(fig)

#
def contourPlotVarOnMapFrame(variable, date, \
                       contours, npts = 20, \
                       figname='figure', frameNum=0, \
                       title='Data', units='units', \
                       width_fac = 16, height_fac = 12):
     import wUUtils as Util
     stations = Util.getStationList()
     data = Util.loadDailyVariable(stations, date, variable)
     contourPlotDataOnMapFrame(data, contours, npts, \
                               figname, frameNum, title, \
                               units, width_fac, height_fac)

###############################################################
################# CONTOUR PLOTS OF DATA ON MAP BACKGROUND #####
###############################################################
#
def VariableWithInset(data, insetData, \
                      contours, npts = 20, \
                      figname='figure', frameNum=0, \
                      title='Data', units='units', \
                      width_fac = 16, height_fac = 12):
     import numpy as np
     import wUUtils as Util
     import matplotlib.pyplot as plt
     import scipy.interpolate
     from mpl_toolkits.basemap import Basemap
     # open new figure window
     fig = plt.figure()
     # get station locations
     lon, lat = Util.getStationLonLat(Util.getStationList())
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
     # load data
     stations = Util.getStationList()
     lon, lat = Util.getStationLonLat(stations)
     # convert data to arrays:
     x, y, z = np.array(lon), np.array(lat), np.array(data)
     print('\nmain axes:')
     print(data)
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
     cs = m.contourf(xi,yi,zi,levels=contours,cmap=plt.cm.jet)
     # add colorbar.
     cbar = m.colorbar(cs,location='bottom',pad="5%")
     cbar.set_label(units)
     plt.title(title)

     # create insets 
     for iax in range(len(insetData)):
          corner = 0.65-0.22*iax
          ax1 = plt.axes([0.7, corner, 0.2, 0.2])

          m1 = Basemap(width=width_fac*100000,height=height_fac*100000, \
                      projection='lcc', resolution='i', \
                      lat_1=45.,lat_0=lat0,lon_0=lon0)

          # draw coastlines.
          m1.drawcoastlines()
          m1.drawcountries()
          m1.drawstates()
          # draw a boundary around the map, fill the background.
          # this background will end up being the ocean color, since
          # the continents/data will be drawn on top.
          m1.drawmapboundary(fill_color='aqua')
          # convert data to arrays:
          x, y, z = np.array(lon), np.array(lat), np.array(insetData[iax])
          # print('\niax ' + str(iax) + ':')
          # print(insetData[iax])
          # map data points to projection coordinates
          xmap, ymap = m1(x,y)
          # Set up a regular grid of interpolation points
          xi, yi = np.linspace(x.min(), x.max(), npts), \
                   np.linspace(y.min(), y.max(), npts)
          # map regular lon-lat grid to projection coordinates
          xi, yi = m1(*np.meshgrid(xi,yi))
          # Interpolate data to projected regular grid 
          # function is one of 'linear', 'multiquadric', 'gaussian',
          #                    'inverse', 'cubic', 'quintic', 'thin_plate'
          rbf1 = scipy.interpolate.Rbf(xmap, ymap, z, \
                                       function='linear')
          zi = rbf1(xi, yi)
          # draw filled contours
          cs1 = m1.contourf(xi,yi,zi,levels=contours,cmap=plt.cm.jet)

     # save plot
     filename = '%s_frame_%03d.png' % (figname, frameNum)
     # print('saving file: ' + filename)
     plt.savefig(filename, bbox_inches='tight')
     plt.close()

