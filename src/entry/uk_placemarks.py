"""
Read the CSV file created by modes.xml2csv.py using placenames.yml.
"""
import argparse
import codecs
from collections import defaultdict
import csv
from haversine import haversine, Unit
import json
import re
import sys

WHR_LOCATION = (51.5920, -0.3870)  # lat, lng
MERGEDPLACENAMES_P = 'results/entry/mergedplacenames.pickle'


def load_placemarks(incsv, ldplacemarks):

    placemarks = {}
    zerolat = set()
    for row in incsv:
        lat = float(row['lat'])
        long = float(row['long'])
        name = row['place15nm'].lower()
        if lat == 0:
            zerolat.add(name)
            continue
        newdistance = haversine(WHR_LOCATION, (lat, long), unit=Unit.MILES)
        if name not in placemarks or newdistance < placemarks[name]:
            placemarks[name] = newdistance
    # print(f'number with zero lat: {len(zerolat)}')
    # for name in zerolat:
    #     print(name)
    if ldplacemarks:
        nadded = 0
        for ldp in ldplacemarks:
            if ldp not in placemarks:
                nadded += 1
                placemarks[ldp] = ldplacemarks[ldp][0]
        print(f'London placemarks added: {nadded}')
    print(f'Total placemarks: {len(placemarks)}')
    return placemarks


def recode_place(placename):
    if _args.norecode:
        return None
    if placename == 'local':
        return 'pinner'
    return None


def process_survey(insurveycsv, placemarks, outdistfile):
    numrow = numok = numblank = 0
    notfound = defaultdict(int)
    for row in insurveycsv:
        numrow += 1
        wherefrom = row['wherefrom'].strip().lower()
        if not wherefrom:
            numblank += 1
            continue
        if wherefrom not in placemarks:
            recoded_place = recode_place(wherefrom)
            if recoded_place is None or recoded_place not in placemarks:
                notfound[wherefrom] += 1
                continue
            wherefrom = recoded_place
        distance = placemarks[wherefrom]
        datestr = row['date']
        print(f'{datestr},{wherefrom},{distance}', file=outdistfile)
        numok += 1
    if _args.notfound:
        nffile = open(_args.notfound, 'w')
        for name in notfound:
            print(f'{notfound[name]:03},"{name}"', file=nffile)
    print(f'Total records: {numrow}')
    print(f'not found:{sum(notfound.values())}, unique not found: '
          f'{len(notfound)}, blank: {numblank}, ok: {numok}')


def main():
    ldplacemarks = None
    if _args.json:
        with open(_args.json) as jsonfile:
            ldplacemarks = json.load(jsonfile)
            print(f'{len(ldplacemarks)} London placemarks loaded from '
                  f'{_args.json}')
    with codecs.open(_args.inlocation, 'r', 'utf-8-sig') as inlocfile:
        inloccsv = csv.DictReader(inlocfile, delimiter='|')
        placemarks = load_placemarks(inloccsv, ldplacemarks)
    with codecs.open(_args.insurvey, 'r', 'utf-8-sig') as insurveyfile:
        outdistfile = open(_args.outdistance, 'w')
        insurveycsv = csv.DictReader(insurveyfile)
        process_survey(insurveycsv, placemarks, outdistfile)


def getargs():
    parser = argparse.ArgumentParser(description='''
        Extract placenames from the placemark file and compute distance from
        the museum.
        ''')
    parser.add_argument('inlocation', help='''
         The input CSV file containing location data.''')
    parser.add_argument('insurvey', help='''
         The input CSV file containing survey data.''')
    parser.add_argument('outdistance', help='''
         The output CSV file containing distance data.''')
    parser.add_argument('-j', '--json',
                        help='''input JSON file of London placemarks.
        ''')
    parser.add_argument('-n', '--notfound',
                        help='''output CSV file of not found placenames.
        ''')
    parser.add_argument('--norecode', action='store_true',
                        help='''Inhibit recoding of names not found.
        ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    Modify verbosity.
    ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 8)
    _args = getargs()
    if _args.verbose > 1:
        print(f'verbosity: {_args.verbose}')
    print(f'Input: {_args.inlocation}')
    main()
