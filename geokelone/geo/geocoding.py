# -*- coding: utf-8 -*-
"""
Unit tests for the library.
"""


import logging
import re
# import sys

from heapq import nlargest
from math import radians, cos, sin, asin, sqrt

from .. import settings


# logging
logger = logging.getLogger(__name__)

if settings.FILTER_LEVEL == 1:
    MAX_CANDIDATES = 5
elif settings.FILTER_LEVEL == 2 or settings.FILTER_LEVEL == 3:
    MAX_CANDIDATES = 10

vicinity = settings.DISAMBIGUATION_SETTING[settings.STANDARD_SETTING]['vicinity']
reference = settings.DISAMBIGUATION_SETTING[settings.STANDARD_SETTING]['reference']

i = 0
results = dict()
common_names = set() # use wikt-to-dict
stoplist = set()
lines = list()
lastcountry = ''
pair = list()
pair_counter = 0

# logger.info('settings: %s', settings.MINLENGTH)



def haversine(lat1, lon1, lat2, lon2):
# http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points#4913653
    """
    Calculate the great circle distance between two points on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    logger.debug('raw distance in km: %s', km)
    # sufficient resolution for most calculations, locations in a city may require more
    returnval = "{0:.2f}".format(km)
    logger.debug('estimated distance in km: %s', returnval)
    return returnval


def disambiguate(candidates, step, metainfo):
    """
    Determine the most probable entry among candidates.
    """
    # test if list
    if not isinstance(candidates, list):
        logger.error('type, not a list: %s', ' '.join(candidates))
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
        distances[candidate] = haversine(reference[0], reference[1], float(metainfo[candidate][0]), float(metainfo[candidate][1]))
        # population
        if int(metainfo[candidate][4]) > 1000:
            scores[candidate] += 1
        # vicinity
        if metainfo[candidate][3] in vicinity:
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


def geofind(name, codesdict, metainfo):
    """
    Find the token(s) in the gazzetteer
    """
    ## TODO: change return value from True to something else
    # check
    if name not in codesdict:
        # not found
        # print('ERROR, not found:', name)
        return True
    # else
    winning_id = ''
    # single winner
    if not isinstance(codesdict[name], list) or len(codesdict[name]) == 1:
        winning_id = codesdict[name][0]
        logger.info('winner: %s', codesdict[name])
    # hopefully find the right one
    else:
        winning_id = disambiguating_rounds(name, codesdict, metainfo)
        if winning_id is True:
            return True

    store_result(winning_id, name, metainfo)
    # return "found"
    return False


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
        return True
    # init
    global i
    # 3-step filter
    step = 1
    while step <= 3:
        # launch function
        if step == 1:
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
            return True
        # found
        if not isinstance(winners, list):
            winning_id = winners
            break
                # if len(winners) == 1
    ## TODO: NEVER HAPPENS??
    if winning_id is None:
        try:
            logger.warning('too many winners: %s %s', name, winners)
        except UnicodeEncodeError:
            logger.warning('too many winners + unicode error: %s', winners)
        i += 1
        return True

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

    ## frequency counts
    # disable frequency count if multi-word on
    #if multiflag is False:
    #    freq = '{0:.4f}'.format(tokens[name]/numtokens)
    #else:
    #    freq = '0'
    freq = 'NULL'
    # TODO: test id/name

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

    # TODO: implement here
    #elif name not in common_names and name.lower() not in common_names and name in level4:
    #    templist = [level4[name][0], level4[name][1], '4', 'NULL', 'NULL', name] # level4[name][0]

    # canonical result
        canonname = templist[-1]
        # results
        # store whole result or just count
        if canonname not in results:
            # disable frequency count if multi-word on
            #if multiflag is False:
            #    freq = '{0:.4f}'.format(tokens[canonname]/numtokens)
            #else:
            #    freq = '0'
            freq = 'NULL'
            results[canonname] = templist
            results[canonname].append(freq)
            results[canonname].append(1)
        else:
            # increment last element
            results[canonname][-1] += 1
        # lines flag
        if settings.LINESBOOL is True:
            draw_line(templist[0], templist[1])
        # store flag
        return False
    # else
    return True


def search(searchlist, codesdict, metainfo, custom_lists=None):
    """
    Geocoding: search if valid place name and assign coordinates.
    """
    # init
    global pair_counter
    global results
    results = dict()
    slide2 = ''
    slide3 = ''
    pair_counter = 0

    # search for places
    for token in searchlist:
        keep_running = True
        if token == ' ':
            continue
        # skip and reinitialize:
        if token == 'XXX' or re.match(r'[.,;:–]', token): # St–?
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
        if settings.VERBOSITY == 'V':
            ## TODO: verbosity control
            logger.info('%s %s %s', token, slide2, slide3)

        ## analyze sliding window first, then token if necessary
        # longest chain first
        if len(slide3) > 0 and slide3.count(' ') == 2:
            # selected lists first
            if custom_lists is not None:
                keep_running = selected_lists(slide3, custom_lists)
            # if nothing has been found
            if keep_running is True and slide3 not in stoplist:
                keep_running = geofind(slide3, codesdict, metainfo)
        # longest chain first
        if keep_running is True and len(slide2) > 0 and slide2.count(' ') == 1:
            # selected lists first
            if custom_lists is not None:
                keep_running = selected_lists(slide2, custom_lists)
            # if nothing has been found
            if keep_running is True and slide2 not in stoplist:
                keep_running = geofind(slide2, codesdict, metainfo)
        # just one token, if nothing has been found
        if keep_running is True:
            if len(token) >= settings.MINLENGTH and not re.match(r'[a-zäöü]', token) and token not in stoplist:
            # and (tokens[token]/numtokens) < threshold
                if custom_lists is not None:
                    keep_running = selected_lists(token, custom_lists)
                # dict check before
                if keep_running is True and token not in common_names and token.lower() not in common_names:
                    keep_running = geofind(token, codesdict, metainfo)

        # final check whether to keep the multi-word scan running
        if keep_running is False:
            slide2 = ''
            slide3 = ''

        pair_counter += 1
    # return something
    return results


# draw lines
def draw_line(lat, lon):
    """
    Draw lines between points on the map.
    """
    global pair, lines, pair_counter
    if pair_counter <= settings.CONTEXT_THRESHOLD:
        if len(pair) == 1:
            pair.append((lat, lon))
            lines.append((pair[0], pair[1]))
            del pair[0]
        else:
            pair.append((lat, lon))
    else:
        pair = []
        pair.append((lat, lon))
    pair_counter = 0
