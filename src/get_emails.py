"""
get_emails.py - Read the CSV file that has been exported from SurveyMonkey
and update our database of email addresses.

Print new addresses.


"""

import argparse
import csv
import os.path
import sys

import jsonutil

DBPATH = os.path.join('data', 'email_addrs')
WANT_NEWSLETTER_COL = 277
WANT_NOTIFY_COL = 278
VOLUNTEER_COL = 279
EMAIL_ADDR_COL = 283

NEWSLETTER = 'newsletter'
VOLUNTEER = 'volunteer'


def init_dbdict():
    return {
        NEWSLETTER: {},
        VOLUNTEER: {}
    }


def main(csvfilename):
    # Use dictionaries instead of sets because json doesn't support sets
    new_newsletter_dict = {}
    new_volunteer_dict = {}
    nrow = 3
    dbdict = jsonutil.load_json(DBPATH)
    if not dbdict:
        dbdict = init_dbdict()
    old_len_newsletter = len(dbdict[NEWSLETTER])
    old_len_volunteer = len(dbdict[VOLUNTEER])
    with open(csvfilename, newline='') as csvfile:
        monkeyreader = csv.reader(csvfile)
        for n in range(3):
            next(monkeyreader)
        for row in monkeyreader:
            nrow += 1
            want_newsletter = row[WANT_NEWSLETTER_COL].strip()
            want_notify = row[WANT_NOTIFY_COL].strip()
            want_volunteer = row[VOLUNTEER_COL].strip()
            email_addr = row[EMAIL_ADDR_COL].strip()
            if want_newsletter or want_notify or want_volunteer:
                if not email_addr:
                    print('email address missing, row', nrow)
                    continue
            if want_newsletter or want_notify:
                if email_addr not in dbdict[NEWSLETTER]:
                    new_newsletter_dict[email_addr] = 0
                    dbdict[NEWSLETTER][email_addr] = 0
            if want_volunteer:
                if email_addr not in dbdict[VOLUNTEER]:
                    new_volunteer_dict[email_addr] = 0
                    dbdict[VOLUNTEER][email_addr] = 0
    print('Wants newsletter:')
    for addr in sorted(new_newsletter_dict):
        print('  ', addr)
    print('Wants to volunteer:')
    for addr in sorted(new_volunteer_dict):
        print('  ', addr)
    jsonutil.save_json(dbdict, DBPATH)

if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main(sys.argv[1])
