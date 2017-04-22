import datetime
import json
import os

MAXJSONFILES = 10  # The number of JSON files to save. Older ones are deleted.


def load_json(dbpath):
    """
    Iterate over the JSON files in DBPATH, find the most recent one.
    :return: The loaded dictionary.
    """
    files = os.listdir(dbpath)
    pcdict = {}
    jsonfilename = None
    for f in sorted(files, reverse=True):
        print('-->', f)
        if f.endswith('.json'):
            jsonfilename = os.path.join(dbpath, f)
            break
    try:
        with open(jsonfilename) as jsonfile:
            print('Loading database file {}'.format(jsonfilename))
            pcdict = json.load(jsonfile)
            print('{} records loaded'.format(len(pcdict)))
    except TypeError:  # if no files found
        print('No files found in {}'.format(dbpath))
    return pcdict


def save_json(pcdict, dbpath, starttime=None):
    """
    Create a JSON file in the DBPATH directory and delete any old JSON files
    found.

    :param pcdict: the dictionary containing the postcode data.
    :param dbpath: the path to the directory to save the JSON file in.
    :param starttime: the datetime object to use in creating the json file name
    :return: None
    """
    os.makedirs(dbpath, exist_ok=True)
    if not starttime:
        starttime = datetime.datetime.today()
    filename = starttime.strftime("%Y%m%d-%H%M%S.json")
    filepath = os.path.join(dbpath, filename)
    with open(filepath, 'w') as jsonfile:
        json.dump(pcdict, jsonfile, indent=4)
    print('{} records saved to {}.'.format(len(pcdict), filename))
    # delete old json files
    files = sorted(os.listdir(dbpath))
    files = [f for f in files if f.endswith('.json')]
    if len(files) <= MAXJSONFILES:
        return
    for f in files[:len(files) - MAXJSONFILES]:
        os.remove(os.path.join(dbpath, f))
        print('Deleting ', os.path.join(dbpath, f))
