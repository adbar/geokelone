#!/usr/bin/python3


import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
# import numpy as np


from .. import settings

from ..data import validators


## TODO:
# points types
# ..
# http://scitools.org.uk/cartopy/docs/latest/matplotlib/feature_interface.html
# http://scitools.org.uk/cartopy/docs/latest/matplotlib/intro.html?highlight=ccrs%20geodetic
# http://scitools.org.uk/cartopy/docs/latest/gallery.html



# not all projections need this
# standard_parallels = (45, 63)
# central_longitude = -1 # -(91 + 52 / 60)
# projection=ccrs.LambertConformal(central_longitude=central_longitude, standard_parallels=standard_parallels))



def draw_map(filename, results):
    """
    Place points/lines on a map and save it in a file.
    """
    fig = plt.figure()

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mollweide(central_longitude=0, globe=None))

    if settings.FIXED_FRAME is True:
        ax.set_extent([settings.WESTMOST, settings.EASTMOST, settings.SOUTHMOST, settings.NORTHMOST])
    else:
        print('## ERROR: flexible framing not implemented yet')

    # ax.gridlines()
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAND)
    # ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.COASTLINE)

    for item in results:
        if True: # if validate_mapdata(results[item]) is True
            lat, lon, ptype, country, something, pname, somethingelse, occurrences = results[item]
            lat = float(lat)
            lon = float(lon)
            print('# INFO projecting:', pname, lat, lon)
        else:
            print('# WARN problem with entry:', item)
            continue

        # point
        ax.plot(lon, lat, marker='o', color='green', markersize=2, alpha=0.5, transform=ccrs.Geodetic())
        # text
        geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
        text_transform = offset_copy(geodetic_transform, units='dots', x=-10) # x=-25
        ax.text(lon, lat, pname, verticalalignment='center', horizontalalignment='right', transform=text_transform, fontsize=5)
        # bbox=dict(facecolor='sandybrown', alpha=0.5, boxstyle='round')

    # ax.coastlines(resolution='50m', color='black', linewidth=0.5)

    plt.savefig(filename, dpi=300)
