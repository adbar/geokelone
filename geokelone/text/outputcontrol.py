# -*- coding: utf-8 -*-
"""
Control and print/write results.
"""

import logging

# own
## outdated #  from ..geo import results, lines # datestok
from .. import settings


# logging
logger = logging.getLogger(__name__)


COLUMN_NAMES = ('id', 'latitude', 'longitude', 'type', 'country', 'population', 'place', 'frequency', 'occurrences')


def writefile(outputfile, results, datestok):
    """
    Control and write results to a file.
    """
    with open(outputfile, 'w', encoding='utf-8') as outputfh:
        outputfh.write('\t'.join(COLUMN_NAMES))
        if settings.DATEBOOL is True:
            outputfh.write('\t' + 'dates' + '\n')
        else:
            outputfh.write('\n')

        for key in sorted(results):
            outputfh.write(key)
            for item in results[key]:
                if isinstance(item, list):
                    for subelement in item:
                        outputfh.write('\t' + str(subelement))
                    # dates
                    if settings.DATEBOOL is True:
                        if item[6] in datestok:
                        # filter century
                            dates = datestok[item[6]]
                            if len(dates) == 1:
                                outputfh.write('\t' + dates[0])
                            else:
                                outputfh.write('\t' + '|'.join(dates))
                        else:
                            outputfh.write('\t' + '0')
                else:
                    outputfh.write('\t' + str(item))
            outputfh.write('\n')

def writelines(linesfile, lines):
    """
    Control and write line/collocation data to a file.
    """
    with open(linesfile, 'w') as outputfh:
        outputfh.write('{"type": "FeatureCollection","features": [')
        i = 1
        threshold = int(len(lines)/10) # https://github.com/alexpreynolds/colormaker
        color = 1
        #r = 0
        #g = 255
        #b = 255
        for line in lines:
            (lat1, lon1) = line[0]
            (lat2, lon2) = line[1]
            # htmlcolor = "#%02x%02x%02x" % (r,g,b)
            if i > 1:
                outputfh.write(',')
            outputfh.write('{"geometry": {"type": "LineString", "coordinates":[[')
            outputfh.write(lon1 + ',' + lat1 + '],[' + lon2 + ',' + lat2 + ']]')
            outputfh.write('},"type": "Feature", "properties": { "arc":' + str(i) + ',')
            outputfh.write(' ' + '"start": "' + lon1 + ',' + lat1 + '", "end": "' + lon2 + ',' + lat2 + '", ')
            outputfh.write('"htmlcolor": "' + str(color) + '"}}')

            i += 1
            # affect color spectrum
            if i % threshold == 0:
                color += 1
                # g -= 1

        outputfh.write(']}')
