"""

"""
import argparse
from collections import defaultdict
import codecs
import csv
import sys

VISITORS = 'visitors'

class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def getargs():
    parser = argparse.ArgumentParser(formatter_class=SmartFormatter,
                                     description='''
        Functions for tidying the CSV file.
        ''')
    parser.add_argument('infile', help='''
         The input XLSX file containing multiple tabs.''')
    parser.add_argument('outfile',
                        help='''output CSV file.
        ''')
    parser.add_argument('-f', '--function', type=int, required=True, help='''R|
1. Find non-numeric visitors.
2. .
3. .
    ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    Modify verbosity.
    ''')
    args = parser.parse_args()
    return args


def list_non_numeric_visitors(reader):
    nrow = 1
    for row in reader:
        nrow += 1
        try:
            # Convert the datetime into a date string because the default
            # is to emit the date and time.
            row[VISITORS] = int(row[VISITORS])
        except ValueError:
            print(nrow, ', '.join(row.values()), file=outfile)


def main():
    infile = codecs.open(_args.infile, 'r', 'utf-8-sig')
    reader = csv.DictReader(infile)
    if _args.function == 1:
        list_non_numeric_visitors(reader)
    # elif _args.function == 2:
    #     list_bad_dates(wb)
    # elif _args.function == 3:
    #     merge_sheets(wb)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    if _args.verbose > 1:
        print(f'verbosity: {_args.verbose}')
    print(f'Input: {_args.infile}')
    outfile = codecs.open(_args.outfile, 'w', 'utf-8-sig')
    # writer = csv.writer(outfile)
    main()
