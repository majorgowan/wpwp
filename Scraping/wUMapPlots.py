###############################################################
################## PLOTS ON MAP BACKGROUND ####################
###############################################################
#
# ref: http://matplotlib.org/basemap/users/geography.html
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
     # convert back to lat/lon
     lonpt, latpt = m(xpt,ypt,inverse=True)
     m.plot(xpt,ypt,'bo')  # plot a blue dot there
     for icity in range(len(cityName)):
          plt.text(xpt[icity]+30000,ypt[icity]+20000,cityName[icity])
     plt.show()
     
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

     plt.figure()

     # setup Lambert Conformal basemap.
     m = Basemap(width=1500000,height=1200000,projection='lcc',
            resolution='i',lat_1=45.,lat_0=43.6,lon_0=-82.)
     # draw coastlines.
     m.drawcoastlines()
     m.drawcountries()
     m.drawstates()
     # draw a boundary around the map, fill the background.
     # this background will end up being the ocean color, since
     # the continents will be drawn on top.
     m.drawmapboundary(fill_color='aqua')
     # fill continents, set lake color same as ocean color.
     # m.fillcontinents(color='wheat',lake_color='aqua')
     # convert data to arrays:
     x, y, z = np.array(lon), np.array(lat), np.array(data)
     # Set up a regular grid of interpolation points
     xi, yi = np.linspace(x.min(), x.max(), 20), \
              np.linspace(y.min(), y.max(), 20)
     xi, yi = m(*np.meshgrid(xi,yi))
     #xi, yi = np.meshgrid(xi, yi)
     # Interpolate
     xmap, ymap = m(x,y)
     rbf = scipy.interpolate.Rbf(xmap, ymap, z, function='linear')
     zi = rbf(xi, yi)
     # draw filled contours.
     cs = m.contourf(xi,yi,zi,10,cmap=plt.cm.jet)
     m.scatter(xmap,ymap,c=z)  # plot a dot at real data points
     # add colorbar.
     cbar = m.colorbar(cs,location='bottom',pad="5%")
     cbar.set_label('data')
     # add title
     plt.show()