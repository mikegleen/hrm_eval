import haversine
import json
import requests
import sys
import time

WHR_LOCATION = (51.5920, -.3870)  # lat, lng
URL = 'http://maps.googleapis.com/maps/api/geocode/json'


def get_address(postcode):
    payload = dict(sensor='false')
    address = ''.join(postcode.split())  # remove all whitespace
    payload['address'] = address + ',UK'
    response = requests.get(URL, params=payload)
    return response.json()


def get_distance(postcode):
    """
    :param postcode:
    :return: a tuple consisting of the distance in miles (a float) and the
             formatted address as a string.
    """
    print('trying: ', postcode)
    j = get_address(postcode)
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

    for postcode in postcodefile:
        time.sleep(2)  # google gets annoyed if we hit it too quickly.
        postcode = ''.join(postcode.split())
        if postcode:
            distance, addr = get_distance(postcode)
            print('{:9},{:8.2f}, {}'.format(postcode, distance, addr),
                  file=addressfile)


def one_postcode(postcode):
    postcode = ''.join(postcode.split())
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

