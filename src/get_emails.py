"""
get_emails.py - Read the CSV file that has been exported from SurveyMonkey
and update our database of email addresses.


"""

import csv
import os.path
import sys

DBPATH = os.path.join('data', 'email_addrs')
WANT_NEWSLETTER_COL = 277
WANT_NOTIFY_COL = 278
VOLUNTEER_COL = 279
EMAIL_ADDR_COL = 283


def main(csvfilename):
    # Use dictionaries instead of sets because json doesn't support sets
    newsletter_dict = {}
    volunteer_dict = {}
    nrow = 3
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
                newsletter_dict[email_addr] = 0
            if want_volunteer:
                volunteer_dict[email_addr] = 0
    print('Wants newsletter:')
    for addr in sorted(newsletter_dict):
        print('  ', addr)
    print('Wants to volunteer:')
    for addr in sorted(volunteer_dict):
        print('  ', addr)


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main(sys.argv[1])