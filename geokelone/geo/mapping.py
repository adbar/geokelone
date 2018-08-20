# -*- coding: utf-8 -*-
"""
Rudimentary mapping functions.
"""


# standard
import heapq
import logging
import random

# additional
from adjustText import adjust_text # https://github.com/Phlya/adjustText/
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
# import numpy as np

# custom
from .. import settings
from ..data import validators

# logging
logger = logging.getLogger(__name__)


## TODO:
# settings vs. args
# LogNorm size
# lines: http://scitools.org.uk/cartopy/docs/latest/matplotlib/intro.html?highlight=ccrs%20geodetic



POINT_COLORS = {0: 'brown', 1: 'yellow', 2: 'orange', 3: 'olive', 4: 'blue',}

# not all projections need this
# standard_parallels = (45, 63)
# central_longitude = -1 # -(91 + 52 / 60)
# projection=ccrs.LambertConformal(central_longitude=central_longitude, standard_parallels=standard_parallels))


def normalize(x, minval, maxval, a=1, b=12):
    """
    Normalize value.
    """
    normval = ((b-a)*(x-minval)) / (maxval-minval) + a
    return normval


#def quality_control():
#    """
#    Check if the result can be displayed on the map.
#    """


def examine(results, limitlabels):
    """
    Examine results to determine visualization settings
    """
    occs = list()
    for item in results:
        try:
            lastcol = int(results[item][-1])
            occs.append(lastcol)
        except (TypeError, ValueError):
            logger.warning('wrong value for occurrences: %s', results[item][-1])
    maxval = max(occs)
    minval = min(occs)
    # limit text to top-n elements
    topn = heapq.nlargest(limitlabels, occs)[-1]
    return minval, maxval, topn


def random_placement():
    """
    Examine results to determine visualization settings
    """
    # X
    xchoice = random.choice(['left', 'center', 'right']) # random.choice(['left', 'center', 'right'])
    if xchoice == 'left':
        xval = -30 #xval = random.randint(-20, 20)
    elif xchoice == 'center':
        xval = random.choice([-5, 5])
    elif xchoice == 'right':
        xval = 30
    # Y
    ychoice = random.choice(['bottom', 'center', 'top']) # random.choice(['bottom', 'center', 'top'])
    if ychoice == 'bottom':
        yval = -30 #yval = random.randint(-20, 20)
    elif ychoice == 'center':
        yval = random.choice([-5, 5])
    elif ychoice == 'top':
        yval = 30
    # sum up
    logger.debug('%s %s %s %s', xchoice, xval, ychoice, yval)
    return xval, yval


def draw_map(filename, results, withlabels=True, limitlabels=30, feature_scale=settings.FEATURE_SCALE, relative_markersize=False, adjusted_text=False, simple_map=False, colored=False):
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

    if simple_map is False:
        ocean_feature = cfeature.NaturalEarthFeature('physical', 'ocean', feature_scale, edgecolor='face', facecolor=cfeature.COLORS['water'])
        land_feature = cfeature.NaturalEarthFeature('physical', 'land', feature_scale, edgecolor='face', facecolor=cfeature.COLORS['land']) # land_alt1
        #coastline_feature = cfeature.NaturalEarthFeature('physical', 'coastline', feature_scale, edgecolor='black', facecolor=None)
        ax.add_feature(ocean_feature)
        ax.add_feature(land_feature, alpha=1)
        #ax.add_feature(coastline_feature, alpha=0.1)
    # simpler contours
    else:
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.LAND)
        ## ax.add_feature(cfeature.BORDERS)
        ax.add_feature(cfeature.COASTLINE)

    i = 1
    texts = list()

    ## proportional
    minval, maxval, topn = examine(results, limitlabels)

    # loop through results and draw points on the map
    for item in results:
        if validators.validate_mapdata(results[item], map_boundaries) is True:
            # unused: country, ptype, something, somethingelse
            lat, lon, ptype, _, _, pname, _, occurrences = results[item]
            lat = float(lat)
            lon = float(lon)
            logger.info('projecting: %s %s %s', pname, lat, lon)
        else:
            # logger.warning('problem with entry: %s', item)
            continue

        # point
        # proportional size
        if relative_markersize is False:
            msize = 2
        else:
            msize = normalize(occurrences, minval, maxval)
            # prcfreq = (occurrences/maxval)*100
            # msize = prcfreq/4 # was 10

        # colors
        ## default
        if colored is False:
            pcolor = 'green'
        else:
            if ptype in POINT_COLORS:
                pcolor = POINT_COLORS[ptype]
            else:
                pcolor = 'green'

        # draw point
        ax.plot(lon, lat, marker='o', color=pcolor, markersize=msize, alpha=0.5, transform=ccrs.Geodetic())

        # text
        if withlabels is True and occurrences >= topn: # prcfreq > 5: # was 13
            geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)

            # text adjustment is experimental
            if adjusted_text is True:
                texts.append(ax.text(lon, lat, pname, fontsize=4, horizontalalignment='center', verticalalignment='center', transform=ccrs.Geodetic())) # transform=text_transform, wrap=True
            # normal case
            else:
                xval, yval = random_placement()
                text_transform = offset_copy(geodetic_transform, x=xval, y=yval, units='dots')
                ax.text(lon, lat, pname, verticalalignment=ychoice, horizontalalignment=xchoice, transform=text_transform, fontsize=4, wrap=True,) #  zorder=i

            # text_transform = offset_copy(geodetic_transform, units='dots', x=-10) # x=-25
            # ax.text(lon, lat, pname, verticalalignment='center', horizontalalignment='right', transform=text_transform, fontsize=5)
            # bbox=dict(facecolor='sandybrown', alpha=0.5, boxstyle='round')

        i += 1

    # ax.coastlines(resolution='50m', color='black', linewidth=0.5)

    # proceed at the end
    if adjusted_text is True:
        logger.info('text labels displayed: %s', len(texts))
        # adjust_text(texts, force_points=0.2, force_text=0.2, expand_points=(1,1), expand_text=(1,1), arrowprops=dict(arrowstyle="-", color='black', lw=0.5, alpha=0.5), save_steps=True, save_prefix='step', save_format='png',)
        adjust_text(texts,) # save_steps=True, save_prefix='step', save_format='png',

    # finish
    plt.savefig(filename, dpi=300)
