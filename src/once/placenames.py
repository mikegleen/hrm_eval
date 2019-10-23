# -*- coding: utf-8 -*-
"""
Read a CSV file created by modes/html2csv.py from the downloaded Wikipedia page
of Harrow placenames (entrysurvey/wikip.html).

Extract the placenames in London and placenames in Harrow and create a JSON
file containing a dictionary of the form:
    {
        'locations': <list of names in London>,
        'harrow':    <list of names in Harrow>
    }

"""

import codecs
import csv
import json
import sys

infile = codecs.open(sys.argv[1], 'r', 'utf-8-sig')
outfile = open(sys.argv[2], 'w', newline='')

reader = csv.DictReader(infile)

locations = set()
harrow = set()
for row in reader:
    location = row['Location'].lower()
    borough = row['London\xa0borough'].lower()
    # Process the first column
    loclist = location.split(' (also ')
    locations.add(loclist[0].strip())
    if 'harrow' in borough:
        harrow.add(loclist[0])
    if len(loclist) > 1:
        loclist[1] = loclist[1][:-1]  # strip off trailing ')'
        loc2list = loclist[1].split(',')  # (also this, that)
        for loc in loc2list:
            locations.add(loc.strip())
            if 'harrow' in borough:
                harrow.add(loc.strip())

    # Process the second column
    borough = borough.split('[')[0]  # strip off trailing '[9]'
    borough = borough.split(',')
    for loc in borough:
        locations.add(loc.strip())

locdict = {'locations': sorted(locations), 'harrow': sorted(harrow)}
json.dump(locdict, outfile, indent=4)
print(len(locations), 'placenames found.')
print(len(harrow), 'in Harrow.')
