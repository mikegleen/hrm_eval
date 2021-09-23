"""
Read an XML file containing Placemark elements and extract the name and lat and
long co-ordinates.The format of the element is:
        <Placemark>
            <name><![CDATA[Abbey Wood]]></name>
            <Point>
                <coordinates>0.1109,51.4864,0</coordinates>
            </Point>
            <Snippet></Snippet>
            <description><![CDATA[<br>Source: Wikipedia article <a href="https://en.wikipedia.org/wiki/Abbey_Wood">Abbey Wood</a>]]></description>
        </Placemark>

The code assumes valid data and will barf if anything unexpected is found.
If there are multiple occurances of a placename in different boroughs, we only
keep the one closest to the museum.
"""
import argparse
from collections import namedtuple
from haversine import haversine, Unit
import json
import sys
import xml.etree.ElementTree as et

WHR_LOCATION = (51.5920, -.3870)  # lat, lng

Placemark = namedtuple('Placemark', ('distance', 'borough'))


def getargs():
    parser = argparse.ArgumentParser(description='''
        Functions for tidying the CSV file.
        ''')
    parser.add_argument('infile', help='''
         The input XML file containing location data.''')
    parser.add_argument('-j', '--json',
                        help='''output JSON file.
        ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    Modify verbosity.
    ''')
    args = parser.parse_args()
    return args


def load_placemarks():

    def trace(action):
        if _args.verbose > 1:
            print(f'{action} old: {place}, {oldplace.borough} ('
                  f'{oldplace.distance:.4f}), new: {place}'
                  f', {borough} ({newdistance:.4f})')

    ns = {'kml': "http://earth.google.com/kml/2.1"}
    placemarks = {}
    root = et.parse(_args.infile).getroot()
    document = root.find('kml:Document', ns)
    for placemark in document.findall('kml:Placemark', ns):
        name = placemark.find('./kml:name', ns).text
        coords = placemark.find('./kml:Point/kml:coordinates', ns).text
        places = [place.strip().lower() for place in name.split(',')]
        long, lat, _ = coords.split(',')
        borough = None
        newdistance = haversine(WHR_LOCATION, (float(lat), float(long)),
                                unit=Unit.MILES)
        place = places[0]
        # If there are duplicate placenames in separate boroughs, such as
        # "Hayes, Bromley" and "Hayes, Hillingdon".  We choose the closer one.
        if len(places) > 1:  # there may be multiple placenames
            borough = places[1]
            if place in placemarks:
                oldplace = placemarks[place]
                if newdistance > oldplace.distance:
                    trace('keeping  ')
                    continue
                else:
                    trace('replacing')
        placemarks[place] = Placemark(newdistance, borough)
    return placemarks


def main():
    placemarks = load_placemarks()
    if _args.json:
        with open(_args.json, 'w') as jsonfile:
            json.dump(placemarks, jsonfile, indent=4)
            print(f'{len(placemarks)} rows dumped to {_args.json}')


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    if _args.verbose > 1:
        print(f'verbosity: {_args.verbose}')
    print(f'Input: {_args.infile}')
    main()
