"""
Update our database of postcodes, retaining the distance from the museum.
The database is stored in a JSON file in DBPATH with a name based on the
creation date and time.

Input is a text file with one line per postcode; empty lines are ignored. You
may have to delete the top row(s) when extracting the data from a spreadsheet.

If the postcode from the text file is not in the database, the information is
fetched from google maps.
"""
from collections import namedtuple
import haversine
import os.path
import requests
import sys
import time

import jsonutil

WHR_LOCATION = (51.5920, -.3870)  # lat, lng
URL = 'http://maps.googleapis.com/maps/api/geocode/json'
PcData = namedtuple('PcData', 'distance address count'.split())

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
    print('trying: ', postcode)
    j = get_json(postcode)
    # print(json.dumps(j, indent=4))
    l = j['results'][0]['geometry']['location']
    addr = j['results'][0]['formatted_address']
    location = (l['lat'], l['lng'])
    # print(location)
    distance = haversine.haversine(WHR_LOCATION, location, miles=True)
    return distance, addr


def main(postcodefilename, addressfilename):
    postcodefile = open(postcodefilename)
    addressfile = open(addressfilename, 'w')
    pcdata = jsonutil.load_json(DBPATH)

    for postcode in pcdata:
        pcdata[postcode][2] = 0  # reinitialize counts
    for postcode in postcodefile:
        postcode = ''.join(postcode.split()).upper()
        if not postcode:
            continue
        if postcode in pcdata:
            pcdata[postcode][2] += 1
        else:
            time.sleep(1)  # google gets annoyed if we hit it too quickly.
            try:
                distance, addr = get_distance(postcode)
                pcdata[postcode] = PcData(distance, addr, 1)
            except IndexError:
                print('Error: {} not found, ignored.'.format(postcode))
    for postcode in sorted(pcdata):
        distance = pcdata[postcode][0]
        addr = pcdata[postcode][1]
        count = pcdata[postcode][2]
        if count > 1:
            pcc = postcode + ',{},'.format(count)
            print('{:12}{:8.2f}, "{}"'.format(pcc, distance, addr),
                  file=addressfile)
        else:
            pcc = postcode + ',,'  # to prettyprint
            print('{:12}{:8.2f}, "{}"'.format(pcc, distance, addr),
                  file=addressfile)
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
        if len(sys.argv[1]) > 12:
            print('If one parameter is given, it must be a valid postcode.')
            sys.exit(1)
        row = one_postcode(sys.argv[1])
        print('{},{:8.2f}, {}'.format(*row))

