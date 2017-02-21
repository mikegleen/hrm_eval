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
import matplotlib
from config import skiprows, defcol


def onerow(row, q5col, nrow):
    groupsize = 1
    for n in range(5):
        base = q5col + 5 * n
        if row[base + 4]:  # if not sure
            return None
        if row[base]:
            groupsize += 1
        elif row[base + 1]:
            groupsize += 2
        elif row[base + 2]:
            groupsize += 3
        elif row[base + 3]:
            groupsize += 4
    return groupsize


def print_report(parties, notsure):
    def prints(*data):
        print(*data)
        print(*data, file=reportfile)
    filename = _starttime.strftime("q5stats_%Y%m%d-%H%M%S.txt")
    reportpath = os.path.join(_args.outdir, filename)
    reportfile = open(reportpath, 'w')
    for n in sorted(parties.keys()):
        prints('{:8} {}'.format(n, parties[n]))
    prints('not sure {}'.format(notsure))


def main():
    parties = defaultdict(int)
    csvfilename = _args.infile
    nrow = skiprows
    with open(csvfilename, newline='', encoding='utf-8-sig') as csvfile:
        monkeyreader = csv.reader(csvfile)
        nskip = skiprows - 1
        if skiprows <= 0:  # can only validate if there is a heading
            raise ValueError('The heading must exist to find Q5 column.')
        row = next(monkeyreader)
        q5col = -1
        for n in range(len(row)):
            if row[n] == 'q5':
                q5col = n
                break
        if q5col < 0:
            raise ValueError('Cannot find "q5" in header.')
        for n in range(nskip):
            next(monkeyreader)
        notsure = 0
        for row in monkeyreader:
            nrow += 1
            partysize = onerow(row, q5col, nrow)
            if partysize:
                # print(nrow, partysize)
                parties[partysize] += 1
            else:
                notsure += 1
    print_report(parties, notsure)


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

