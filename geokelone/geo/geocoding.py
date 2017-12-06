# -*- coding: utf-8 -*-
"""
Geocoding and disambiguation functions needed to extract and resolve place names.
"""


import logging
import re
import sys

from heapq import nlargest
from math import radians, cos, sin, asin, sqrt

from .. import settings


# logging
logger = logging.getLogger(__name__)


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


def geofind(name, codesdict, metainfo, custom_lists):
    """
    Find the token(s) in the gazzetteer(s)
    """
    # selected lists first
    if custom_lists is not None:
        stop_search = selected_lists(name, custom_lists)
        if stop_search is True:
            # return "found"
            return True

    # condition to examine
    if len(name) <= settings.MINLENGTH or not name[0].isupper() or name in stoplist:
        return False

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


def search(searchlist, codesdict, metainfo, custom_lists=None):
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
            stop_search = geofind(slide3, codesdict, metainfo, custom_lists)
        # longest chain first
        if stop_search is False and slide2.count(' ') == 1:
            stop_search = geofind(slide2, codesdict, metainfo, custom_lists)
        # just one token, if nothing has been found
        if stop_search is False:
             # dict check before
            if token not in common_names and token.lower() not in common_names:
                stop_search = geofind(token, codesdict, metainfo, custom_lists)
            # TODO: frequency threshold? (tokens[token]/numtokens) < threshold

        # final check whether to keep the multi-word scan running
        if stop_search is True:
            slide2 = ''
            slide3 = ''

        pair_counter += 1
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
