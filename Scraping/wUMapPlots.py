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
     cityName = ['CYYZ', 'CYUL', 'KDTW']
     lon, lat = [-79.6306, -73.7408, -83.3533], [43.6767, 45.4706, 42.2125]
#     lon, lat = -79.6306, 43.6767 # Location of Boulder
     # convert to map projection coords.
     # Note that lon,lat can be scalars, lists or numpy arrays.
     xpt,ypt = m(lon,lat)
     # convert back to lat/lon
     lonpt, latpt = m(xpt,ypt,inverse=True)
     m.plot(xpt,ypt,'bo')  # plot a blue dot there
     for icity in range(3):
          plt.text(xpt[icity]+30000,ypt[icity]+20000,cityName[icity])
     plt.show()