# -*- coding: utf-8 -*-
"""
Geocoding and disambiguation functions needed to extract and resolve place names.
"""


import logging
import re
import sys

from heapq import nlargest
from math import asin, atan, atan2, cos, radians, sin, sqrt, tan
# from sqlitedict import SqliteDict

from .. import settings


# logging
logger = logging.getLogger(__name__)


VICINITY = settings.DISAMBIGUATION_SETTING[settings.STANDARD_SETTING]['vicinity']
REFERENCE = settings.DISAMBIGUATION_SETTING[settings.STANDARD_SETTING]['reference']

i = 0
results = dict()
common_names = set() # use wikt-to-dict
lines = list()
lastcountry = ''
pair = list()
pair_counter = 0

# logger.info('settings: %s', settings.MINLENGTH)

# DB
# DBPATH = './metainfo.sqlite'


def haversine(point1, point2):
    """
    Calculate the great circle distance between two points on the Earth (specified in decimal degrees) using spherical geometry with a mean radius.
    """
    # short-circuit coincident points
    if point1[0] == point1[1] and point2[0] == point2[1]:
        return 0.0
    # http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points#4913653
    # https://github.com/mapado/haversine/
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [point1[0], point1[1], point2[0], point2[1]])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Mean Earth radius according to International Union of Geodesy and Geophysics (WGS 84)
    # Moritz, H. (March 2000). "Geodetic Reference System 1980". Journal of Geodesy. 74 (1): 128–133.
    returnval = 6371.0088 * c
    # returnval = "{0:.3f}".format(km)
    logger.debug('estimated distance in km: %s', returnval)
    return round(returnval, 5)


def vincenty(point1, point2, max_iter=200):
    """
    Calculate the distance between two points on the Earth, Vincenty's solution to the inverse geodetic problem is more accurate that the great circle distance using Haversine formula.
    """
    # T. Vincenty, Direct and inverse solutions of geodesics on the ellipsoid with application of nested equations, Survey Review 23(176), 88–93 (1975).
    # short-circuit coincident points
    if point1[0] == point2[0] and point1[1] == point2[1]:
        return 0.0
    # https://github.com/maurycyp/vincenty
    # init
    # WGS 84
    a = 6378137  # meters
    f = 1 / 298.257223563
    b = 6356752.314245  # meters; b = (1 - f)a
    convergence_threshold = 1e-12

    # process
    U1 = atan((1 - f) * tan(radians(point1[0])))
    U2 = atan((1 - f) * tan(radians(point2[0])))
    L = radians(point2[1] - point1[1])
    Lambda = L
    sinU1 = sin(U1)
    cosU1 = cos(U1)
    sinU2 = sin(U2)
    cosU2 = cos(U2)

    # iterate
    for iteration in range(max_iter):
        sinLambda = sin(Lambda)
        cosLambda = cos(Lambda)
        sinSigma = sqrt((cosU2 * sinLambda) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
        if sinSigma == 0:
            return 0.0  # coincident points
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cosSqAlpha = 1 - sinAlpha ** 2
        try:
            cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha
        except ZeroDivisionError:
            cos2SigmaM = 0
        C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
        LambdaPrev = Lambda
        Lambda = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma *
                                               (cos2SigmaM + C * cosSigma *
                                                (-1 + 2 * cos2SigmaM ** 2)))
        if abs(Lambda - LambdaPrev) < convergence_threshold:
            break  # successful convergence
    else:
        return None  # failure to converge

    uSq = cosSqAlpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
    B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
    deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma *
                 (-1 + 2 * cos2SigmaM ** 2) - B / 6 * cos2SigmaM *
                 (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)))
    s = b * A * (sigma - deltaSigma)

    # return
    s /= 1000  # meters to kilometers
    return round(s, 5)


def disambiguate(candidates, step, metainfo):
    """
    Determine the most probable entry among candidates.
    """
    # test if list
    if not isinstance(candidates, list):
        logger.error('type, not a list: %s, %s', type(candidates), candidates)
        return candidates
    # avoid single items
    if len(candidates) == 1:
        return candidates[0]

    # decisive argument: population
    headcounts = list()
    popdict = dict()
    for candidate in candidates:
        headcounts.append(metainfo[candidate][4])
        popdict[metainfo[candidate][4]] = candidate
    largest = nlargest(2, headcounts)
    # all null but one
    if largest[0] != 0 and largest[1] == 0:
        return popdict[largest[0]]
    # second-largest smaller by a factor of 1000
    if largest[0] > 1000*largest[1]:
        return popdict[largest[0]]

    # points: distance, population, vicinity, last country seen
    scores = dict()
    distances = dict()
    # step 2: filter places with no population
    if step == 2:
        for candidate in candidates:
            if int(metainfo[candidate][4]) == 0:
                candidates.remove(candidate)
    # double entries: place + administrative region
    if len(candidates) == 2:
        if metainfo[candidates[0]][2] == 'A' and metainfo[candidates[1]][2] == 'P':
            return candidates[1]
        elif metainfo[candidates[0]][2] == 'P' and metainfo[candidates[1]][2] == 'A':
            return candidates[0]
    # last country code seen
    #if lastcountry is not None:
    #    if metainfo[item][3] == lastcountry:
    #        scores[item] += 1

    # tests
    for candidate in candidates:
        # init
        scores[candidate] = 0
        # distance: lat1, lon1, lat2, lon2
        # use more precise calculation
        if settings.FILTER_LEVEL == 'MAXIMUM':
            dist = vincenty((REFERENCE[0], REFERENCE[1]), (float(metainfo[candidate][0]), float(metainfo[candidate][1])))
            # fails to converge for nearly antipodal points
            if dist is None:
                dist = haversine((REFERENCE[0], REFERENCE[1]), (float(metainfo[candidate][0]), float(metainfo[candidate][1])))
        # use faster approximation
        else:
            dist = haversine((REFERENCE[0], REFERENCE[1]), (float(metainfo[candidate][0]), float(metainfo[candidate][1])))
        distances[candidate] = dist
        # population
        if int(metainfo[candidate][4]) > 1000:
            scores[candidate] += 1
        # vicinity
        if metainfo[candidate][3] in VICINITY:
            scores[candidate] += 1
    # best distance
    smallest_distance = min(distances.values())
    for number in [k for k, v in distances.items() if v == smallest_distance]:
        scores[number] += 1
    # best score
    best_score = max(scores.values())
    best_ones = [k for k, v in scores.items() if v == best_score]
    # analyze
    if len(best_ones) == 1:
        #if isinstance(best_ones, list):
        return best_ones[0]
        #else:
        #    lastcountry = metainfo[best_ones][3]
    if len(best_ones) == 2:
        # double entries: place + administrative region
        if metainfo[best_ones[0]][2] == 'A' and metainfo[best_ones[1]][2] == 'P':
            return best_ones[1]
        elif metainfo[best_ones[0]][2] == 'P' and metainfo[best_ones[1]][2] == 'A':
            return best_ones[0]


def geofind(name, codesdict, metainfo, custom_lists=None, stoplist=None):
    """
    Find the token(s) in the gazzetteer(s)
    """
    # condition to examine
    if len(name) <= settings.MINLENGTH or not name[0].isupper() or name in stoplist:
        return False

    # selected lists first
    if custom_lists is not None:
        stop_search = selected_lists(name, custom_lists)
        if stop_search is True:
            # return "found"
            # store_result() # already performed above
            return True

    # check
    if name not in codesdict:
        # not found
        # print('ERROR, not found:', name)
        return False
    # else
    winning_id = ''
    # single winner
    if not isinstance(codesdict[name], list) or len(codesdict[name]) == 1:
        winning_id = codesdict[name][0]
        logger.debug('winner: %s', codesdict[name])
    # hopefully find the right one
    else:
        winning_id = disambiguating_rounds(name, codesdict, metainfo)
        if winning_id is None:
            return False

    store_result(winning_id, name, metainfo)

    return True


def disambiguating_rounds(name, codesdict, metainfo):
    """
    Disambiguate between several candidates for the same toponym, in up to three rounds.
    """
    # discard if too many
    if len(codesdict[name]) >= MAX_CANDIDATES:
        try:
            logger.warning('discarded: %s %s', name, codesdict[name])
        except UnicodeEncodeError:
            logger.warning('discarded + unicode error: %s', codesdict[name])
        return None
    # init
    global i
    # 3-step filter
    step = 1
    while step <= 3:
        # launch function
        if step == 1:
            # print(codesdict[name], step, metainfo)
            winners = disambiguate(codesdict[name], step, metainfo)
        else:
            winners = disambiguate(winners, step, metainfo)
        # nothing found
        if winners is None:
            try:
                logger.warning('out of winners: %s %s', name, codesdict[name])
            except UnicodeEncodeError:
                logger.warning('out of winners + unicode error: %s', codesdict[name])
            i += 1
            return None
        # found
        if not isinstance(winners, list):
            winning_id = winners
            break
        elif len(winners) == 1:
            winning_id = winners[0]
            break
    ## TODO: NEVER HAPPENS??
    if winning_id is None:
        try:
            logger.warning('too many winners: %s %s', name, winners)
        except UnicodeEncodeError:
            logger.warning('too many winners + unicode error: %s', winners)
        i += 1
        return None

        # throw dice and record
        #if len(winning_id) == 0:
        #    for element in best_ones:
        #        print(name, element, scores[element], distances[element], str(metainfo[element]), sep='\t')
        #        i += 1
            # random choice to store...
        #    winning_id = choice(best_ones)

    return winning_id


def store_result(winning_id, name, metainfo):
    """
    Store result along with context information.
    """
    # init
    global i, lastcountry, results

    # TODO: frequency counts
    # disable frequency count if multi-word on
    #if multiflag is False:
    #    freq = '{0:.4f}'.format(tokens[name]/numtokens)
    #else:
    #    freq = '0'
    freq = 'NULL'

    # store new result
    if winning_id not in results:
        results[winning_id] = list()
        try:
            for element in metainfo[winning_id]:
                results[winning_id].append(element)
        except KeyError:
            logger.error('key not found: %s', winning_id)
            return True
        results[winning_id].append(name)
        results[winning_id].append(freq)
        results[winning_id].append(1)
    # increment last element
    else:
        results[winning_id][-1] += 1

    # store context info
    lastcountry = metainfo[winning_id][3]

    # lines flag
    if settings.LINESBOOL is True:
        draw_line(results[winning_id][0], results[winning_id][1])

    logger.debug('stored item %s with info %s', winning_id, results[winning_id])
    return


def selected_lists(name, dic):
    """
    Bypass general search by looking into specified registers.
    """
    # init
    global results

    # search + canonicalize
    if name in dic:
        templist = [dic[name]['values'][0], dic[name]['values'][1], dic[name]['level'], 'NULL', 'NULL', dic[name]['values'][2]]
        canonname = dic[name]['values'][2]
        tempdic = {canonname: [dic[name]['values'][0], dic[name]['values'][1], dic[name]['level'], 'NULL', 'NULL']} # canonname
        store_result(canonname, name, tempdic)

        # lines flag
        if settings.LINESBOOL is True:
            draw_line(templist[0], templist[1])

        # store flag
        return True
    # else
    return False


def search(searchlist, codesdict, metainfo, custom_lists=dict(), stoplist=dict()): # dbpath=DBPATH
    """
    Geocoding: search if valid place name and assign coordinates.
    """
    # safety check
    global MAX_CANDIDATES
    if settings.FILTER_LEVEL == 'MAXIMUM':
        MAX_CANDIDATES = 5
    elif settings.FILTER_LEVEL == 'MEDIUM' or settings.FILTER_LEVEL == 'MINIMUM':
        MAX_CANDIDATES = 10
    else:
        logger.error('filter level not correctly set: %s', settings.FILTER_LEVEL)
        sys.exit(1)
    # init
    global pair_counter
    global results
    # metainfo = SqliteDict('./metainfo.sqlite')
    results = dict()
    slide2 = ''
    slide3 = ''
    pair_counter = 0

    # search for places
    for token in searchlist:
        stop_search = False
        if token == ' ':
            continue
        # skip and reinitialize:
        # TODO: quotation marks? brackets?
        if token == 'XXX' or re.match(r'[.!?…,;:–]', token): # St–?
            slide2 = ''
            slide3 = ''
            continue
        ## grow or limit (delete first word)
        # 2-gram
        if len(slide2) == 0:
            slide2 = token
        elif slide2.count(' ') == 0:
            slide2 = slide2 + ' ' + token
        else:
            slide2 = re.sub(r'^.+? ', '', slide2)
            slide2 = slide2 + ' ' + token
        # 3-gram
        if len(slide3) == 0:
            slide3 = token
        #elif slide3.count(' ') < 1:
        #   slide3 = slide3 + ' ' + token
        elif slide3.count(' ') < 2:
            slide3 = slide3 + ' ' + token
        else:
            slide3 = re.sub(r'^.+? ', '', slide3)
            slide3 = slide3 + ' ' + token

        # control
        # if settings.VERBOSITY == 'V':
        logger.debug('%s %s %s', token, slide2, slide3)

        ## analyze sliding window first, then token if necessary
        # longest chain first
        if slide3.count(' ') == 2:
            stop_search = geofind(slide3, codesdict, metainfo, custom_lists, stoplist)
        # longest chain first
        if stop_search is False and slide2.count(' ') == 1:
            stop_search = geofind(slide2, codesdict, metainfo, custom_lists, stoplist)
        # just one token, if nothing has been found
        if stop_search is False:
             # dict check before
            if token not in common_names and token.lower() not in common_names:
                stop_search = geofind(token, codesdict, metainfo, custom_lists, stoplist)
            # TODO: frequency threshold? (tokens[token]/numtokens) < threshold

        # final check whether to keep the multi-word scan running
        if stop_search is True:
            slide2 = ''
            slide3 = ''

        pair_counter += 1
    # db
    # metainfo.close()
    # return something
    return results


# draw lines
## TODO: test and evaluate
def draw_line(lat, lon):
    """
    Draw lines between points on the map.
    """
    global pair, lines, pair_counter
    logger.debug('line drawing check: %s %s %s %s', pair, pair_counter, lat, lon)
    if pair_counter <= settings.CONTEXT_THRESHOLD:
        if len(pair) == 1:
            pair.append((lat, lon))
            lines.append((pair[0], pair[1]))
            logger.debug('line drawn: %s', (pair[0], pair[1]))
            del pair[0]
        else:
            pair.append((lat, lon))
            logger.debug('line component added: %s', (lat, lon))
    else:
        logger.debug('context size exceeded (%s), pair reset', pair_counter)
        pair = []
        pair.append((lat, lon))
        logger.debug('line component added: %s', (lat, lon))
    pair_counter = 0
