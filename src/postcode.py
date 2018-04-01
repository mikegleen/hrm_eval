"""
Update our database of postcodes, retaining the distance from the museum.
The database is stored in a JSON file in DBPATH with a name based on the
creation date and time.

Input is the CSV file exported from SurveyMonkey with options "expanded" and
"actual".

If the postcode from the CSV file is not in the database, the information is
fetched from google maps.

Output is a new JSON file in the same directory as the input file but with the
current date/time. Also output is a report in the file named in parameter 2.
The oldest JSON file is deleted if there are more than 5 of them.
"""
from collections import namedtuple
import csv
import haversine
import os.path
import requests
import sys
import time

# local imports
import config
import jsonutil

WHR_LOCATION = (51.5920, -.3870)  # lat, lng
POSTCODE_COL = config.defcol['postcode']
URL = 'https://maps.googleapis.com/maps/api/geocode/json'
# replace PcData with simple list because we now need to update the count.
# PcData = namedtuple('PcData', 'distance address count'.split())
PATCHES = {'W5': 'W5,LONDON',
           'CM': 'CM,CHELMSFORD'}
"""
    The DBPATH directory contains the latest JSON files with the most recently
    created table of postcode data.
"""
DBPATH = os.path.join('data', 'postcode')


def get_json(postcode):
    """
    Fetch this postcode's JSON formatted data from Google.

    :param postcode: UK Postcode with all white space removed.
    :return: The dictionary of the JSON string returned by requests.
    """
    payload = dict(sensor='false')
    payload['address'] = postcode + ',UK'
    response = requests.get(URL, params=payload)
    if response.status_code != 200:
        print('Retrying ' + postcode)
        time.sleep(5)
        response = requests.get(URL, params=payload)
        if response.status_code != 200:
            raise IOError('status {} returned'.format(response.status_code))
    return response.json()


def get_distance(postcode):
    """
    :param postcode:
    :return: a tuple consisting of the distance in miles (a float) and the
             formatted address as a string.
    """
    if postcode in PATCHES:
        print('patching: {}->{}'.format(postcode, PATCHES[postcode]))
        postcode = PATCHES[postcode]
    print('get_distance: ', postcode)
    j = get_json(postcode)
    # print(json.dumps(j, indent=4))
    l = j['results'][0]['geometry']['location']
    addr = j['results'][0]['formatted_address']
    location = (l['lat'], l['lng'])
    # print(location)
    distance = haversine.haversine(WHR_LOCATION, location, miles=True)
    return distance, addr


def main(postcodefilename, reportfilename):
    postcodefile = open(postcodefilename, newline='')
    monkeyreader = csv.reader(postcodefile)
    for n in range(config.SKIPROWS):
        next(monkeyreader)

    reportfile = open(reportfilename, 'w')
    pcdata = jsonutil.load_json(DBPATH)

    for postcode in pcdata:
        pcdata[postcode][2] = 0  # reinitialize counts
    for row in monkeyreader:
        postcode = row[POSTCODE_COL]
        postcode = ''.join(postcode.split()).upper()  # remove embedded spaces
        if not postcode:
            continue
        if postcode in pcdata:
            pcdata[postcode][2] += 1
        else:
            time.sleep(1)  # google gets annoyed if we hit it too quickly.
            try:
                distance, addr = get_distance(postcode)
                # pcdata[postcode] = PcData(distance, addr, 1)
                pcdata[postcode] = [distance, addr, 1]
            except IndexError:
                print('Error: {} not found, ignored.'.format(postcode))
    for postcode in sorted(pcdata):
        distance = pcdata[postcode][0]
        addr = pcdata[postcode][1]
        count = pcdata[postcode][2]
        if count > 1:
            pcc = postcode + ',{},'.format(count)
            print('{:12}{:8.2f}, "{}"'.format(pcc, distance, addr),
                  file=reportfile)
        else:
            pcc = postcode + ',,'  # to prettyprint
            print('{:12}{:8.2f}, "{}"'.format(pcc, distance, addr),
                  file=reportfile)
    jsonutil.save_json(pcdata, DBPATH)


def one_postcode(postcode):
    postcode = ''.join(postcode.split()).upper()
    try:
        distance, addr = get_distance(postcode)
    except IndexError:
        return postcode, 0, "**** NOT FOUND ****"
    return postcode, distance, addr

if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        if len(sys.argv[1]) > 20:
            print('If one parameter is given, it must be a valid postcode.')
            sys.exit(1)
        result = one_postcode(sys.argv[1])
        print('{},{:8.2f}, {}'.format(*result))

