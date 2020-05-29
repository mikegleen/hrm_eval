"""

"""
import codecs
import csv
from haversine import haversine, Unit
import json
import pickle
import sys
import time

WHR_LOCATION = (51.5920, -0.3870)  # lat, lng
UKPLACENAMES = 'results/entry/ukplacenames.csv'
OUTCODES = 'data/entry/postcode-outcodes.csv'
MERGEDPLACENAMES = 'results/entry/mergedplacenames.json'
MERGEDPLACENAMES_P = 'results/entry/mergedplacenames.pickle'


def load_placemarks(incsv):
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
    print(f'Total placemarks: {len(placemarks)}')
    return placemarks


def load_outcodes(incsv):
    outcodes = {}
    zerolat = set()
    for row in incsv:
        lat = float(row['latitude'])
        long = float(row['longitude'])
        name = row['postcode'].lower()
        if lat == 0:
            # print(row)
            zerolat.add(name)
            continue
        newdistance = haversine(WHR_LOCATION, (lat, long), unit=Unit.MILES)
        if name not in outcodes or newdistance < outcodes[name]:
            outcodes[name] = newdistance
    print(f'Total outcodes: {len(outcodes)}')
    if zerolat:
        print(f'{len(zerolat)} postcodes with zero latitude found.')
    return outcodes


def main():
    # t1 = time.time()
    with codecs.open(UKPLACENAMES, 'r', 'utf-8-sig') as inlocfile:
        inloccsv = csv.DictReader(inlocfile, delimiter='|')
        placemarks = load_placemarks(inloccsv)
    # t2 = time.time()
    # print(t2 - t1)
    with codecs.open(OUTCODES, 'r', 'utf-8-sig') as outcodesfile:
        outcodescsv = csv.DictReader(outcodesfile)
        outcodes = load_outcodes(outcodescsv)
        placemarks.update(outcodes)
    # t1 = time.time()
    with open(MERGEDPLACENAMES_P, 'wb') as mergedfile:
        pickle.dump(placemarks, mergedfile, pickle.HIGHEST_PROTOCOL)
    # print(time.time() - t1)
    # with open(MERGEDPLACENAMES, 'w') as mergedfile:
    #     json.dump(placemarks, mergedfile)



if __name__ == '__main__':
    assert sys.version_info >= (3, 8)
    main()
