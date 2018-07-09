# -*- coding: utf-8 -*-
"""
Rudimentary mapping functions.
"""


# standard
import logging
import random

# additional
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
# import numpy as np

from adjustText import adjust_text # https://github.com/Phlya/adjustText/

# custom
from .. import settings
from ..data import validators


# logging
logger = logging.getLogger(__name__)


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





def draw_map(filename, results, withlabels=True, feature_scale=settings.FEATURE_SCALE, relative_markersize=False, adjusted_text=False):
    """
    Place points/lines on a map and save it in a file.
    """

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mollweide(central_longitude=0, globe=None))
    map_boundaries = [settings.WESTMOST, settings.EASTMOST, settings.SOUTHMOST, settings.NORTHMOST]

    if settings.FIXED_FRAME is True:
        ax.set_extent(map_boundaries)
    else:
        logger.error('flexible framing not implemented yet')

    # ax.gridlines()
    ocean_feature = cfeature.NaturalEarthFeature('physical', 'ocean', feature_scale, edgecolor='face', facecolor=cfeature.COLORS['water'])
    land_feature = cfeature.NaturalEarthFeature('physical', 'land', feature_scale, edgecolor='face', facecolor=cfeature.COLORS['land']) # land_alt1
    #coastline_feature = cfeature.NaturalEarthFeature('physical', 'coastline', feature_scale, edgecolor='black', facecolor=None)
    ax.add_feature(ocean_feature)
    ax.add_feature(land_feature, alpha=1)
    #ax.add_feature(coastline_feature, alpha=0.1)

    #ax.add_feature(cfeature.OCEAN)
    #ax.add_feature(cfeature.LAND)
    ## ax.add_feature(cfeature.BORDERS)
    #ax.add_feature(cfeature.COASTLINE)

    i = 1
    texts = list()

    # proportional
    # maxval = 0
    # if relative_markersize is True:
    occs = list()
    for item in results:
        _, _, _, _, _, _, _, occurrences = results[item]
        occs.append(occurrences)
    maxval = max(occs)
            

    for item in results:
        if validators.validate_mapdata(results[item], map_boundaries) is True:
            # unused: country, ptype, something, somethingelse
            if len(results[item]) != 8:
                logger.error('bad format for result: %', results[item])
                continue
            lat, lon, _, _, _, pname, _, occurrences = results[item]
            lat = float(lat)
            lon = float(lon)
            logger.info('projecting: %s %s %s', pname, lat, lon)
        else:
            # logger.warning('problem with entry: %s', item)
            continue

        # point
        # proportional size
        prcfreq = (occurrences/maxval)*100
        normfreq = prcfreq/4 # was 10
        if relative_markersize is False:
            msize = 2
        else:
            msize = normfreq
        # draw
        ax.plot(lon, lat, marker='o', color='green', markersize=msize, alpha=0.5, transform=ccrs.Geodetic())
        # markersize=2

        # text
        if withlabels is True and prcfreq > 13:
            geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)

            # text adjustment is experimental
            if adjusted_text is True:
                texts.append(ax.text(lon, lat, pname, fontsize=4, wrap=True,)) # transform=text_transform, wrap=True,
            # normal case
            else:
                xchoice = random.choice(['left', 'center', 'right']) # random.choice(['left', 'center', 'right'])
                if xchoice == 'left':
                    xval = -30
                elif xchoice == 'center':
                    xval = random.choice([-5, 5])
                elif xchoice == 'right':
                    xval = 30
                ychoice = random.choice(['bottom', 'center', 'top']) # random.choice(['bottom', 'center', 'top'])
                if ychoice == 'bottom':
                    yval = -30
                elif ychoice == 'center':
                    yval = random.choice([-5, 5])
                elif ychoice == 'top':
                    yval = 30
                #xval = random.randint(-20, 20)
                #yval = random.randint(-20, 20)
                logger.debug('%s %s %s %s', xchoice, xval, ychoice, yval)
                text_transform = offset_copy(geodetic_transform, x=xval, y=yval, units='dots')
                ax.text(lon, lat, pname, verticalalignment=ychoice, horizontalalignment=xchoice, transform=text_transform, fontsize=4, wrap=True,) #  zorder=i

            # text_transform = offset_copy(geodetic_transform, units='dots', x=-10) # x=-25
            # ax.text(lon, lat, pname, verticalalignment='center', horizontalalignment='right', transform=text_transform, fontsize=5)
            # bbox=dict(facecolor='sandybrown', alpha=0.5, boxstyle='round')

        i += 1

    # ax.coastlines(resolution='50m', color='black', linewidth=0.5)

    # proceed at the end
    if adjusted_text is True:
        print(texts)
        adjust_text(texts, force_points=0.2, force_text=0.2, expand_points=(1,1), expand_text=(1,1), arrowprops=dict(arrowstyle="-", color='black', lw=0.5, alpha=0.5), save_steps=True, save_prefix='step', save_format='png',)

    # finish
    plt.savefig(filename, dpi=300)
