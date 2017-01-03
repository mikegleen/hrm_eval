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
import datetime
import haversine
import json
import os.path
import requests
import sys
import time

WHR_LOCATION = (51.5920, -.3870)  # lat, lng
URL = 'http://maps.googleapis.com/maps/api/geocode/json'
PcData = namedtuple('PcData', 'distance address'.split())

"""
    The DBPATH directory contains the latest JSON files with the most recently
    created table of postcode data.
"""
DBPATH = os.path.join('data', 'postcode')


def load_json():
    """
    Iterate over the JSON files in DBPATH, find the most recent one.
    :return: The loaded dictionary.
    """
    files = os.listdir(DBPATH)
    pcdict = {}
    jsonfilename = None
    for f in sorted(files, reverse=True):
        print('-->', f)
        if f.endswith('.json'):
            jsonfilename = os.path.join(DBPATH, f)
            break
    try:
        with open(jsonfilename) as jsonfile:
            print('Loading database file {}'.format(jsonfilename))
            pcdict = json.load(jsonfile)
            print('{} postcodes loaded'.format(len(pcdict)))
    except TypeError:  # if no files found
        print('No files found in {}'.format(DBPATH))
    return pcdict


def save_json(pcdict):
    filename = datetime.datetime.today().strftime("%Y%m%d-%H%M%S.json")
    filepath = os.path.join(DBPATH, filename)
    with open(filepath, 'w') as jsonfile:
        json.dump(pcdict, jsonfile, indent=4)
    print('{} postcodes saved to {}.'.format(len(pcdict), filename))


def get_json(postcode):
    """
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
    pcdata = load_json()
    save_pcdata_len = len(pcdata)
    for postcode in postcodefile:
        time.sleep(1)  # google gets annoyed if we hit it too quickly.
        postcode = ''.join(postcode.split()).upper()
        if postcode and postcode not in pcdata:
            distance, addr = get_distance(postcode)
            pcdata[postcode] = PcData(distance, addr)
    for postcode in sorted(pcdata):
        distance = pcdata[postcode][0]
        addr = pcdata[postcode][1]
        print('{:9},{:8.2f}, {}'.format(postcode, distance, addr),
              file=addressfile)
    if len(pcdata) > save_pcdata_len:
        save_json(pcdata)


def one_postcode(postcode):
    postcode = ''.join(postcode.split()).upper()
    distance, addr = get_distance(postcode)
    return postcode, distance, addr

if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        row = one_postcode(sys.argv[1])
        print('{},{:8.2f}, {}'.format(*row))

