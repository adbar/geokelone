## TODO: activate geonames function

import re

from heapq import nlargest
from math import radians, cos, sin, asin, sqrt

# from ..data import load # to be replaced

verbosebool = True
linesbool = False
minlength = 4
#if filter_level == 1:
#    maxcandidates = 5 # was 10
#elif filter_level == 2 or filter_level == 3:
#    maxcandidates = 10 # was 10
maxcandidates = 10

vicinity = set(['AT', 'BE', 'CH', 'CZ', 'DK', 'FR', 'LU', 'NL', 'PL'])
reference = (float(51.86666667), float(12.64333333)) # Wittenberg

i = 0
results = dict()
dictionary = set()
stoplist = set()
lines = list()



# calculate distance
## source: http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points#4913653
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return "{0:.1f}".format(km)

def find_winner(candidates, step, metainfo):
    # test if list
    if not isinstance(candidates, list):
        print ('ERROR: not a list', candidates)
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
    for number in [k for k,v in distances.items() if v == smallest_distance]:
        scores[number] += 1
    # best score
    best_score = max(scores.values())
    best_ones = [k for k,v in scores.items() if v == best_score]
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

# dict search
def filter_store(name, multiflag, codesdict, metainfo):

    # double check for stoplist
    if name in stoplist:
        return True
    # else
    global i, lastcountry, results
    winning_id = ''
    if name in codesdict:
        # single winner
        if not isinstance(codesdict[name], list) or len(codesdict[name]) == 1:
            winning_id = codesdict[name][0]
        else:
            # discard if too many
            if len(codesdict[name]) >= maxcandidates:
                try:
                    print ('WARN, discarded:', name, codesdict[name])
                except UnicodeEncodeError:
                    print ('WARN, discarded:', 'unicode error', codesdict[name])
                return True
            # 3-step filter
            step = 1
            while (step <= 3):
                # launch function
                if step == 1:
                    winners = find_winner(codesdict[name], step, metainfo)
                else:
                    winners = find_winner(winners, step, metainfo)
                # analyze result
                if winners is None:
                    try:
                        print ('ERROR, out of winners:', name, codesdict[name])
                    except UnicodeEncodeError:
                        print ('ERROR, out of winners:', 'unicode error', codesdict[name])
                    i += 1
                    return True
                if not isinstance(winners, list):
                    winning_id = winners
                    break
                # if len(winners) == 1
            if winning_id is None: ## NEVER HAPPENS??
                try:
                    print ('ERROR, too many winners:', name, winners)
                except UnicodeEncodeError:
                    print ('ERROR, too many winners:', 'unicode error', winners)

                i += 1
                return True

        # throw dice and record
        #if len(winning_id) == 0:
        #    for element in best_ones:
        #        print (name, element, scores[element], distances[element], str(metainfo[element]), sep='\t')
        #        i += 1
            # random choice to store...
        #    winning_id = choice(best_ones)

        # disable frequency count if multi-word on
        #if multiflag is False:
        #    freq = '{0:.4f}'.format(tokens[name]/numtokens)
        #else:
        #    freq = '0'
        freq = 'NULL'
        # store result
        if winning_id not in results:
            results[winning_id] = list()
            try:
                for element in metainfo[winning_id]:
                    results[winning_id].append(element)
            except KeyError:
                print ('ERROR, not found:', winning_id)
                return True
            results[winning_id].append(name)
            results[winning_id].append(freq)
            results[winning_id].append(1)
        else:
            # increment last element
            results[winning_id][-1] += 1
        lastcountry = metainfo[winning_id][3]

        # lines flag
        if linesbool is True:
            draw_line(results[winning_id][0], results[winning_id][1])

        # result
        return False
    else:
        # not found
        # print ('ERROR, not found:', name)
        return True


## search in selected databases
def selected_lists(name, multiflag):
    # init
    global results
    templist = None

    # search + canonicalize
    ## this is ugly
    try:
        if name in level0:
            templist = [level0[name][0], level0[name][1], '0', 'NULL', 'NULL', level0[name][2]]
        elif name in level1:
            templist = [level1[name][0], level1[name][1], '1', 'NULL', 'NULL', level1[name][2]]
        elif name in level2:
            templist = [level2[name][0], level2[name][1], '2', 'NULL', 'NULL', level2[name][2]]
        elif name in level3:
            templist = [level3[name][0], level3[name][1], '3', 'NULL', 'NULL', level3[name][2]]
    # filter here?
    #    elif name not in dictionary and name.lower() not in dictionary and name in level4:
    #        templist = [level4[name][0], level4[name][1], '4', 'NULL', 'NULL', name] # level4[name][0]
    except NameError:
        pass

    # canonical result
    if templist is not None:
        canonname = templist[-1]

    # results
    if templist is not None:
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
        if linesbool is True:
            draw_line(templist[0], templist[1])
        # store flag
        return False
    else:
        return True


def search(searchlist, codesdict, metainfo):
    # init
    slide2 = ''
    slide3 = ''
    pair_counter = 0
    # search for places
    for token in searchlist:
        flag = True
        if token == ' ':
            continue
        # skip and reinitialize:
        if token == 'XXX' or re.match(r'[.,;:–]', token): # St.? -/–?
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
        if verbosebool is True:
            print (token, slide2, slide3, sep=';')

        # flag test
        #if args.prepositions is True:
        #if multiword_flag is False:
        #    if token == 'aus' or token == 'bei' or token == 'bis' or token == 'durch' or token == 'in' or token == 'nach' or token == u'über' or token == 'von' or token == 'zu':
                # print (token)
        #        multiword_flag = True

        ## analyze sliding window first, then token if necessary
        # longest chain first
        if len(slide3) > 0 and slide3.count(' ') == 2:
            # selected lists first
            flag = selected_lists(slide3, True)
            # if nothing has been found
            if flag is True:
                flag = filter_store(slide3, True, codesdict, metainfo)
        # longest chain first
        if flag is True and len(slide2) > 0 and slide2.count(' ') == 1:
            # selected lists first
            flag = selected_lists(slide2, True)
            # if nothing has been found
            if flag is True:
                flag = filter_store(slide2, True, codesdict, metainfo)
        # just one token, if nothing has been found
        if flag is True:
            if len(token) >= minlength and not re.match(r'[a-zäöü]', token) and token not in stoplist:
            # and (tokens[token]/numtokens) < threshold
                flag = selected_lists(token, False)
                # dict check before
                if flag is True and token not in dictionary and token.lower() not in dictionary:
                    flag = filter_store(token, False, codesdict, metainfo)
        
        # final check whether to keep the multi-word scan running
        if flag is False:
            slide2 = ''
            slide3 = ''

        #            if re.match(r'[A-ZÄÖÜ]', token, re.UNICODE):
        #                tempstring = token

        pair_counter += 1
    # return something
    return results


# draw lines
def draw_line(lat, lon):
    global pair, lines, pair_counter
    if pair_counter <= context_threshold:
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


