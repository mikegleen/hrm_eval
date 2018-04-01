"""
q5_stat.py - Compute the average group size from question 5.

input: CSV file name

Question 5 is broken down by age group:
    Under 16
    16 - 34
    35 - 54
    55 - 64
    65 or over

For each age group, there are five values:
1, 2, 3, 4 or over, not sure



"""
import argparse
from collections import defaultdict
import csv
import datetime
import os.path
import sys
from config import SKIPROWS


def getgroupsize(row, q5col):
    groupsize = 1
    for n in range(5):
        base = q5col + 5 * n
        if row[base + 4]:  # if not sure
            return None
        for j in range(4):
            if row[base + j]:
                groupsize += j + 1
                break
    return groupsize


def print_report(parties, notsure, q3q5conflict):
    def prints(*data):
        print(*data)
        # noinspection PyTypeChecker
        print(*data, file=reportfile)
    filename = _starttime.strftime("q5stats_%Y%m%d-%H%M%S.txt")
    reportpath = os.path.join(_args.outdir, filename)
    reportfile = open(reportpath, 'w')
    for n in sorted(parties.keys()):
        prints('{:8} {:4}'.format(n, parties[n]))
    prints('not sure {:4}'.format(notsure))
    prints('conflict {:4}'.format(q3q5conflict))


def findcol(value, row):
    col = -1
    for n in range(len(row)):
        if row[n] == value:
            col = n
            break
    if col < 0:
        raise ValueError('Cannot find "{}" in header.'.format(value))
    return col


def main():
    parties = defaultdict(int)
    nrow = SKIPROWS
    notsure = 0
    q3q5conflict = 0
    if SKIPROWS <= 0:
        raise ValueError('The heading must exist to find Q5 column.')
    with open(_args.infile, newline='', encoding='utf-8-sig') as csvfile:
        monkeyreader = csv.reader(csvfile)
        row = next(monkeyreader)
        q3col = findcol('q3', row)
        q5col = findcol('q5', row)
        for n in range(SKIPROWS - 1):
            next(monkeyreader)
        for row in monkeyreader:
            nrow += 1
            partysize = getgroupsize(row, q5col)
            if partysize:
                # print(nrow, partysize)
                # Check that q3, did you come with someone else, was answered
                # consistent with the q5 answer. The respondent could have said
                # yes and not ticked any boxes in q5 or skipped q3. In either
                # case we ignore that respondent.
                if partysize == 1 and not row[q3col + 1].strip():
                    q3q5conflict += 1
                    continue
                parties[partysize] += 1
            else:
                notsure += 1
    print_report(parties, notsure, q3q5conflict)


def getargs():
    parser = argparse.ArgumentParser(
        description='''
        Read the CSV file that has been exported from
        SurveyMonkey and compute the average group size from question 5.
        ''')
    parser.add_argument('infile', help='''
    The CSV file that has been cleaned by remove_nuls.py, merge_csv.py, and
    clean_title.py''')
    parser.add_argument('-o', '--outdir', default='results', help='''
        Directory to contain the
        output report file. If omitted, the default is the directory
        "results".
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    _starttime = datetime.datetime.today()
    _args = getargs()
    main()

