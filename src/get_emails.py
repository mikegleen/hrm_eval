"""
get_emails.py - Read the CSV file that has been exported from SurveyMonkey
and update our database of email addresses.

Print new email addresses to a file in:
    results/new_emails/emails_<date>-<time>.txt.

input: CSV file name

"""
import argparse
import csv
import datetime
import os.path
import sys

import jsonutil
from config import SKIPROWS, defcol

DBPATH = os.path.join('data', 'email_addrs')
DEFAULT_OUTDIR = os.path.join('results', 'new_emails')
WANT_NEWSLETTER_COL = defcol['want_newsletter']
WANT_NOTIFY_COL = defcol['want_notify']
VOLUNTEER_COL = defcol['volunteer']
EMAIL_ADDR_COL = defcol['email_addr']
# The following is the text inserted by clean_title.py in the first row of the
# column containing the email address. This may change if the survey is
# modified, so we use it to validate the input.
EMAIL_QUESTION = 'q22'

NEWSLETTER = 'newsletter'
VOLUNTEER = 'volunteer'


def init_dbdict():
    return {
        NEWSLETTER: {},
        VOLUNTEER: {}
    }


def onerow(row, nrow, dbdict, new_newsletter_dict, new_volunteer_dict):
    rtn = False  # return True if we've found a new email address
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
            raise ValueError('Invalid email address in row {}: "{}"'.
                             format(nrow, email_addr))
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
    def prints(*data):
        print(*data)
        if not _args.dryrun:
            # noinspection PyTypeChecker
            print(*data, file=reportfile)
    filename = _starttime.strftime("emails_%Y%m%d-%H%M%S.txt")
    csvfilename = _starttime.strftime("emails_%Y%m%d-%H%M%S.csv")
    reportpath = os.path.join(args.outdir, filename)
    csvpath = os.path.join(args.outdir, csvfilename)
    print('Writing report to:', reportpath)
    print('Writing csv file for MailChimp to:', csvpath)
    if not _args.dryrun:
        reportfile = open(reportpath, 'w')
        csvfile = open(csvpath, 'w')
    prints('Wants newsletter:')
    if not len(new_newsletter_dict):
        prints('  ', 'none')
    for addr in sorted(new_newsletter_dict):
        prints('  ', addr)
        if not _args.dryrun:
            print(addr, file=csvfile)
    prints('Wants to volunteer:')
    if not len(new_volunteer_dict):
        prints('  ', 'none')
    for addr in sorted(new_volunteer_dict):
        prints('  ', addr)


def main(args):
    need_update = False
    csvfilename = args.infile
    # Use dictionaries instead of sets because json doesn't support sets
    new_newsletter_dict = {}
    new_volunteer_dict = {}
    nrow = SKIPROWS
    dbdict = jsonutil.load_json(DBPATH)
    if not dbdict:
        print('Initializing database.')
        dbdict = init_dbdict()
    with open(csvfilename, newline='') as csvfile:
        monkeyreader = csv.reader(csvfile)
        nskip = SKIPROWS
        if SKIPROWS > 0:  # can only validate if there is a heading
            row = next(monkeyreader)
            if row[EMAIL_ADDR_COL].strip() != EMAIL_QUESTION:
                raise ValueError('Validation check fails. Col {} of first row'
                                 ' not equal to {}'.
                                 format(EMAIL_ADDR_COL, EMAIL_QUESTION))
            nskip -= 1
        for n in range(nskip):
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
        jsonutil.save_json(dbdict, DBPATH, starttime=_starttime)


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
    parser.add_argument('-o', '--outdir', default=DEFAULT_OUTDIR,
                        help='''Directory to contain the
        output report file. If omitted, the default is the directory
        "results/new_emails" in the same directory that the input file resides.
        ''')
    parser.add_argument('-y', '--dryrun', action='store_true', help='''
    If specified, do not update the database.''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    _starttime = datetime.datetime.today()
    _args = getargs()
    main(_args)
