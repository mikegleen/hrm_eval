"""
get_emails.py - Read the CSV file that has been exported from SurveyMonkey
and update our database of email addresses.

Print new addresses.

input: CSV file name

"""

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


def main(csvfilename):
    # Use dictionaries instead of sets because json doesn't support sets
    new_newsletter_dict = {}
    new_volunteer_dict = {}
    nrow = skiprows
    dbdict = jsonutil.load_json(DBPATH)
    if not dbdict:
        dbdict = init_dbdict()
    with open(csvfilename, newline='') as csvfile:
        monkeyreader = csv.reader(csvfile)
        for n in range(skiprows):
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
                # SurveyMonkey has validated the email address format. If this
                # test fails, probably the CSV format is bad, so quit here.
                if '@' not in email_addr:
                    print('invalid email address in row {}: "{}"'.format(
                        nrow, email_addr
                    ))
                    sys.exit(1)
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
