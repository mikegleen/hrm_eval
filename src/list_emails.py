import argparse
import datetime
import json
import os.path
import sys
import jsonutil

DBPATH = os.path.join('data', 'email_addrs')
NEWSLETTER = 'newsletter'
VOLUNTEER = 'volunteer'


def print_report(new_newsletter_dict, new_volunteer_dict):
    def prints(*data):
        print(*data)
        print(*data, file=reportfile)
    filename = _starttime.strftime("all_emails_%Y%m%d-%H%M%S.txt")
    reportpath = os.path.join(_args.outdir, filename)
    reportfile = open(reportpath, 'w')
    prints('Wants newsletter:')
    for addr in sorted(new_newsletter_dict):
        prints('  ', addr)
    prints('Wants to volunteer:')
    for addr in sorted(new_volunteer_dict):
        prints('  ', addr)


def main():
    if _args.infile:
        with open(_args.infile) as jsonfile:
            dbdict = json.load(jsonfile)
    else:
        dbdict = jsonutil.load_json(DBPATH)
    newsletter = dbdict[NEWSLETTER]
    volunteer = dbdict[VOLUNTEER]
    print_report(newsletter, volunteer)


def getargs():
    parser = argparse.ArgumentParser(
        description='''
        Read the JSON file of the email addresses from the survey and list
        the contents.''')
    parser.add_argument('-i', '--infile', help='''
    If specified, the JSON file containing the data. If omitted, the newest
    file in {} is used.'''.format(DBPATH))
    parser.add_argument('-o', '--outdir', help='''Directory to contain the
        output report file. If omitted, the default is the directory
        "results" in the same directory that the input file resides.
        ''')
    args = parser.parse_args()
    if not args.outdir:
        args.outdir = 'results'
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    _starttime = datetime.datetime.today()
    _args = getargs()
    main()

