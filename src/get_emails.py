"""
get_emails.py - Read the CSV file that has been exported from SurveyMonkey
and update our database of email addresses.

Print new addresses.

input: CSV file name

"""
import argparse
import csv
import os.path
import sys

import jsonutil
from config import skiprows, defcol

DBPATH = os.path.join('data', 'email_addrs')
WANT_NEWSLETTER_COL = defcol['want_newsletter']
WANT_NOTIFY_COL = defcol['want_notify']
VOLUNTEER_COL = defcol['volunteer']
EMAIL_ADDR_COL = defcol['email_addr']

NEWSLETTER = 'newsletter'
VOLUNTEER = 'volunteer'


def init_dbdict():
    return {
        NEWSLETTER: {},
        VOLUNTEER: {}
    }


def onerow(row, nrow, dbdict, new_newsletter_dict, new_volunteer_dict):
    rtn = False
    want_newsletter = row[WANT_NEWSLETTER_COL].strip()
    want_notify = row[WANT_NOTIFY_COL].strip()
    want_volunteer = row[VOLUNTEER_COL].strip()
    email_addr = row[EMAIL_ADDR_COL].strip()
    if want_newsletter or want_notify or want_volunteer:
        if not email_addr:
            print('email address missing, row', nrow)
            return
        # SurveyMonkey has validated the email address format. If this
        # test fails, probably the CSV format is bad, so quit here.
        if '@' not in email_addr:
            print('Invalid email address in row {}: "{}"'.format(
                nrow, email_addr
            ))
            sys.exit(1)
    if want_newsletter or want_notify:
        if email_addr not in dbdict[NEWSLETTER]:
            rtn = True
            new_newsletter_dict[email_addr] = 0
            dbdict[NEWSLETTER][email_addr] = 0
    if want_volunteer:
        if email_addr not in dbdict[VOLUNTEER]:
            rtn = True
            new_volunteer_dict[email_addr] = 0
            dbdict[VOLUNTEER][email_addr] = 0
    return rtn


def print_report(args, new_newsletter_dict, new_volunteer_dict):
    reportfile = open(args.report, 'w')
    print('Wants newsletter:')
    print('Wants newsletter:', file=reportfile)
    for addr in sorted(new_newsletter_dict):
        print('  ', addr)
        print('  ', addr, file=reportfile)
    print('Wants to volunteer:')
    print('Wants to volunteer:', file=reportfile)
    for addr in sorted(new_volunteer_dict):
        print('  ', addr)
        print('  ', addr, file=reportfile)


def main(args):
    need_update = False
    csvfilename = args.infile
    # Use dictionaries instead of sets because json doesn't support sets
    new_newsletter_dict = {}
    new_volunteer_dict = {}
    nrow = skiprows
    dbdict = jsonutil.load_json(DBPATH)
    if not dbdict:
        print('Initializing database.')
        dbdict = init_dbdict()
    with open(csvfilename, newline='') as csvfile:
        monkeyreader = csv.reader(csvfile)
        for n in range(skiprows):
            next(monkeyreader)
        for row in monkeyreader:
            nrow += 1
            rowstat = onerow(row, nrow, dbdict,
                             new_newsletter_dict,
                             new_volunteer_dict)
            need_update = need_update or rowstat
    print_report(args, new_newsletter_dict, new_volunteer_dict)
    if not need_update:
        print('No new addresses. Database not updated.')
    elif args.dryrun:
        print('Dry run. Database not updated.')
    else:
        jsonutil.save_json(dbdict, DBPATH)


def getargs():
    parser = argparse.ArgumentParser(
        description='''
        Read the CSV file that has been exported from
        SurveyMonkey and update our database of email addresses. Also,
        produce a report of the new email addresses of people who have
        requested a newsletter or a volunteer application.''')
    parser.add_argument('infile', help='''
    The CSV file that has been cleaned by remove_nuls.py, merge_csv.py, and
    clean_title.py''')
    parser.add_argument('-r', '--report', default='report.txt', help='''
    The name of the file to contain the report of new email addresses.''')
    parser.add_argument('-y', '--dryrun', action='store_true', help='''
    If specified, do not update the database.''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    _args = getargs()
    main(_args)
